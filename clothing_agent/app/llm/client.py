"""Minimal Groq chat-completions client."""

from __future__ import annotations

import json
import re
from typing import TypeVar

import httpx
from pydantic import BaseModel
from typing import Literal

from app.core.config import AgentConfig
from app.core.errors import DependencyUnavailableError

T = TypeVar("T", bound=BaseModel)


class LLMMessage(BaseModel):
    """One chat-completion message."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, object]] | None = None
    tool_call_id: str | None = None

class LLMResponse(BaseModel):
    """The assistant's response, which may include text or tool calls."""
    content: str | None = None
    tool_calls: list[dict[str, object]] | None = None


class LLMClient:
    """Generate text and validated JSON through Groq's compatible API."""

    def __init__(self, config: AgentConfig, http: httpx.AsyncClient) -> None:
        self._config = config
        self._http = http

    @property
    def configured(self) -> bool:
        """Return whether an API key is available."""

        return self._config.llm_api_key is not None

    async def generate_response(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[dict[str, object]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Return the assistant's response, supporting tool calls."""

        payload = await self._complete(
            messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        try:
            message = payload["choices"][0]["message"] # type: ignore[index]
            return LLMResponse(
                content=message.get("content"),
                tool_calls=message.get("tool_calls"),
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise DependencyUnavailableError(
                "The LLM returned an incomplete response.",
                code="LLM_INVALID_RESPONSE",
            ) from exc

    async def generate_structured(
        self,
        messages: list[LLMMessage],
        response_model: type[T],
    ) -> T:
        """Return a Pydantic-validated JSON object.

        JSON-object mode is used instead of strict JSON Schema mode because the
        routing and extraction contracts contain optional fields and should
        work consistently across Groq chat models.
        """

        schema = response_model.model_json_schema()
        schema_instruction = LLMMessage(
            role="system",
            content=(
                "Return exactly one JSON object matching this schema. Do not "
                f"add markdown or prose:\n{json.dumps(schema)}"
            ),
        )
        payload = await self._complete(
            [*messages, schema_instruction],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = self._content(payload).strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I)
        try:
            return response_model.model_validate_json(content)
        except Exception as exc:
            match = re.search(r"\{.*\}", content, flags=re.S)
            if not match:
                raise DependencyUnavailableError(
                    "The LLM returned an invalid structured response.",
                    code="LLM_INVALID_RESPONSE",
                ) from exc
            try:
                return response_model.model_validate(json.loads(match.group(0)))
            except Exception as nested:
                raise DependencyUnavailableError(
                    "The LLM returned an invalid structured response.",
                    code="LLM_INVALID_RESPONSE",
                ) from nested

    async def _complete(
        self,
        messages: list[LLMMessage],
        *,
        response_format: dict[str, object] | None = None,
        tools: list[dict[str, object]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, object]:
        """Execute one OpenAI-compatible chat-completions request."""

        if not self._config.llm_api_key:
            raise DependencyUnavailableError(
                "The LLM API key is not configured.", code="LLM_NOT_CONFIGURED"
            )
        formatted_messages = []
        for msg in messages:
            m = {"role": msg.role, "content": msg.content or ""}
            if msg.name is not None:
                m["name"] = msg.name
            if msg.tool_calls is not None:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id is not None:
                m["tool_call_id"] = msg.tool_call_id
            formatted_messages.append(m)

        payload: dict[str, object] = {
            "model": self._config.llm_model,
            "messages": formatted_messages,
            "temperature": self._config.llm_temperature if temperature is None else temperature,
            "max_tokens": max_tokens or self._config.llm_max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {
            "Authorization": f"Bearer {self._config.llm_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        try:
            response = await self._http.post(
                self._config.llm_api_base.rstrip("/") + "/chat/completions",
                headers=headers,
                json=payload,
                timeout=self._config.llm_timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                error_data = exc.response.json().get("error", {})
                if error_data.get("code") == "tool_use_failed" and "failed_generation" in error_data:
                    gen = error_data["failed_generation"]
                    import re
                    import uuid
                    
                    match = re.search(r"<function=([a-zA-Z0-9_]+)\s*(\{.*?\})\s*(?:>)?\s*</function>", gen, re.DOTALL)
                    if match:
                        text_before = gen[:match.start()].strip()
                        tool_name = match.group(1)
                        tool_args = match.group(2)
                        
                        logger.info("Recovered from malformed LLM tool generation.")
                        return {
                            "choices": [{
                                "message": {
                                    "role": "assistant",
                                    "content": text_before if text_before else None,
                                    "tool_calls": [{
                                        "id": f"call_{uuid.uuid4().hex[:8]}",
                                        "type": "function",
                                        "function": {
                                            "name": tool_name,
                                            "arguments": tool_args
                                        }
                                    }]
                                }
                            }]
                        }
                    else:
                        text_only = re.sub(r"<function=.*?</function>", "", gen, flags=re.DOTALL).strip()
                        if text_only:
                            logger.info("Recovered conversational text from malformed LLM output.")
                            return {
                                "choices": [{
                                    "message": {
                                        "role": "assistant",
                                        "content": text_only
                                    }
                                }]
                            }
            except Exception:
                pass

            logger.error(f"LLM API Error: {exc.response.text}")
            raise DependencyUnavailableError(
                "The LLM service is currently unavailable.",
                details={"error": f"{exc.response.status_code} from {self._config.llm_api_base}"},
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise DependencyUnavailableError(
                "The LLM service is currently unavailable.",
                code="LLM_UNAVAILABLE",
            ) from exc

    @staticmethod
    def _content(payload: dict[str, object]) -> str:
        """Extract assistant content from an OpenAI-compatible response."""

        try:
            choices = payload["choices"]
            first = choices[0]  # type: ignore[index]
            message = first["message"]  # type: ignore[index]
            content = message["content"]  # type: ignore[index]
        except (KeyError, IndexError, TypeError) as exc:
            raise DependencyUnavailableError(
                "The LLM returned an incomplete response.",
                code="LLM_INVALID_RESPONSE",
            ) from exc
        return content if isinstance(content, str) else str(content)
