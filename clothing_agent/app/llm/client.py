"""Provider-neutral LLM contracts and an OpenAI-compatible implementation.

The Agent depends on the small ``LLMClient`` protocol rather than a specific
model vendor.  This keeps Fitzy deployable against an API model now and a
local OpenAI-compatible model later without changing the orchestration layer.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):
    """Minimal interface required by Fitzy's runtime."""

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
    ) -> T:
        """Generate and validate a structured response."""

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """Generate a natural-language response."""


class LLMConfigurationError(RuntimeError):
    """Raised when the configured LLM provider is missing required settings."""


class LLMResponseError(RuntimeError):
    """Raised when an LLM response cannot be normalized or validated."""


class OpenAICompatibleLLMClient:
    """Call an OpenAI-compatible chat-completions endpoint.

    The implementation intentionally uses ordinary HTTP rather than a vendor
    SDK.  That allows the same Agent to run against OpenAI, a compatible proxy,
    or a local model server that exposes the same API shape.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 45.0,
    ) -> None:
        self._base_url = (base_url or os.getenv("FITZY_LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self._api_key = api_key or os.getenv("FITZY_LLM_API_KEY")
        self._model = model or os.getenv("FITZY_LLM_MODEL")
        self._timeout = timeout_seconds

    def _validate_configuration(self) -> None:
        if not self._api_key:
            raise LLMConfigurationError("FITZY_LLM_API_KEY is not configured")
        if not self._model:
            raise LLMConfigurationError("FITZY_LLM_MODEL is not configured")

    async def _chat(self, *, system_prompt: str, user_message: str, json_mode: bool) -> str:
        self._validate_configuration()
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.1,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/chat/completions", headers=headers, json=payload)
            if response.is_error:
                raise LLMResponseError(f"LLM HTTP {response.status_code}: {response.text[:500]}")
            data = response.json()

        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError("LLM response did not contain chat completion content") from exc

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
    ) -> T:
        """Generate JSON, extract the first JSON object if needed, and validate it."""

        raw = await self._chat(system_prompt=system_prompt, user_message=user_message, json_mode=True)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if not match:
                raise LLMResponseError("LLM did not return a JSON object") from None
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise LLMResponseError("LLM returned malformed JSON") from exc

        try:
            return response_model.model_validate(payload)
        except ValidationError as exc:
            raise LLMResponseError(f"LLM structured output validation failed: {exc}") from exc

    async def generate_text(self, *, system_prompt: str, user_message: str) -> str:
        """Generate plain natural-language text."""

        return await self._chat(system_prompt=system_prompt, user_message=user_message, json_mode=False)


class FakeLLMClient:
    """Deterministic test double used by Phase 4 tests."""

    def __init__(self, structured_response: BaseModel, text_response: str) -> None:
        self.structured_response = structured_response
        self.text_response = text_response
        self.structured_calls: list[tuple[str, str]] = []
        self.text_calls: list[tuple[str, str]] = []

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
    ) -> T:
        self.structured_calls.append((system_prompt, user_message))
        return response_model.model_validate(self.structured_response.model_dump())

    async def generate_text(self, *, system_prompt: str, user_message: str) -> str:
        self.text_calls.append((system_prompt, user_message))
        return self.text_response
