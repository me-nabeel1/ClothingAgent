"""Response formatting and language guardrails for Fitzy."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .state import LanguageMode
from ..llm.client import LLMClient, LLMResponseError
from ..llm.prompts import build_response_system_prompt

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


class ResponseGuard:
    """Validate and, when necessary, regenerate unsafe language output."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def generate(
        self,
        *,
        language: LanguageMode,
        user_message: str,
        runtime_context: Mapping[str, Any],
    ) -> str:
        """Generate a customer-facing response and reject Devanagari output."""

        context_text = str(dict(runtime_context))
        prompt = build_response_system_prompt(language=language.value)
        response = await self._llm.generate_text(
            system_prompt=prompt,
            user_message=(
                f"Customer message:\n{user_message}\n\n"
                f"Authoritative runtime context and tool results:\n{context_text}"
            ),
        )

        if language != LanguageMode.ENGLISH and DEVANAGARI_RE.search(response):
            retry_prompt = (
                f"{prompt}\n\nHARD SAFETY RULE: Your previous response contained Devanagari. "
                f"Generate the same useful answer again using {'Urdu script' if language == LanguageMode.URDU_SCRIPT else 'Roman Urdu'} only."
            )
            response = await self._llm.generate_text(
                system_prompt=retry_prompt,
                user_message=(
                    f"Customer message:\n{user_message}\n\n"
                    f"Authoritative runtime context and tool results:\n{context_text}"
                ),
            )

        if DEVANAGARI_RE.search(response):
            raise LLMResponseError("Unsafe Devanagari/Hindi output detected after regeneration")

        return response.strip()
