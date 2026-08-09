"""General sales-concierge behavior."""

from __future__ import annotations

from app.agents.schemas import AgentRequest, AgentResult
from app.core.config import AgentConfig
from app.core.errors import DependencyUnavailableError
from app.core.routing import Intent
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SALES_PROMPT


class SalesAgent:
    """Handle greetings, general shopping help, and domain redirection."""

    def __init__(self, llm: LLMClient, config: AgentConfig) -> None:
        self._llm = llm
        self._config = config

    async def handle(self, request: AgentRequest) -> AgentResult:
        """Return a concise salesperson response without unsupported claims."""

        if request.route.intent == Intent.OUT_OF_DOMAIN:
            return AgentResult(
                reply="I’m here for clothing, styling, and shopping help. What are you looking to wear?",
                suggested_actions=["I need an outfit", "Help me choose a shirt"],
            )

        if self._llm.configured:
            messages = [LLMMessage(role="system", content=SALES_PROMPT)]
            for item in request.context.messages[-self._config.recent_message_limit :]:
                messages.append(LLMMessage(role=item.role, content=item.content))
            try:
                reply = await self._llm.generate_text(
                    messages,
                    max_tokens=90,
                )
                return AgentResult(reply=reply.strip())
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise

        text = request.message.strip().lower()
        if request.route.intent == Intent.GREETING:
            if "morning" in text:
                reply = "Good morning! What are you shopping for today?"
            elif "afternoon" in text or "evening" in text:
                reply = "Good day! What can I help you find?"
            elif text.startswith("hey"):
                reply = "Hey! What kind of look are you after?"
            else:
                reply = "Hi! What are you shopping for today?"
            return AgentResult(reply=reply)

        return AgentResult(
            reply="Tell me what you’re shopping for, and I’ll help narrow it down.",
            suggested_actions=["I want a shirt", "I need an outfit", "Style advice"],
        )
