"""Intent routing for the sales agent."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from typing import Any

from app.core.conversation import ConversationState
from app.core.errors import DependencyUnavailableError
from app.llm.client import LLMClient, LLMMessage
from pydantic import BaseModel, Field

from .config import AgentConfig


class Intent(StrEnum):
    GREETING = "GREETING"
    GENERAL_SHOPPING_HELP = "GENERAL_SHOPPING_HELP"
    PRODUCT_SEARCH = "PRODUCT_SEARCH"
    PRODUCT_SELECTION = "PRODUCT_SELECTION"
    FIND_SIMILAR = "FIND_SIMILAR"
    PRODUCT_DETAILS = "PRODUCT_DETAILS"
    AVAILABILITY_CHECK = "AVAILABILITY_CHECK"
    FASHION_ADVICE = "FASHION_ADVICE"
    CART_VIEW = "CART_VIEW"
    CART_ADD = "CART_ADD"
    CART_UPDATE = "CART_UPDATE"
    CART_REMOVE = "CART_REMOVE"
    CART_CLEAR = "CART_CLEAR"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    CLARIFICATION = "CLARIFICATION"


class AgentName(StrEnum):
    SALES = "sales_agent"
    SHOPPING = "shopping_agent"
    FASHION = "fashion_agent"
    CART = "cart_agent"


class RouteDecision(BaseModel):
    intent: Intent
    target_agent: AgentName
    confidence: float = Field(default=1.0, ge=0, le=1)
    entities: dict[str, Any] = Field(default_factory=dict)
    requires_clarification: bool = False
    clarification_question: str | None = None
    out_of_domain: bool = False


CLOTHING_TERMS = {
    "shirt", "shirts", "trouser", "trousers", "pants", "jeans", "shorts",
    "tshirt", "t-shirt", "tee", "hoodie", "jacket", "dress", "outfit",
    "clothes", "clothing", "fashion", "style", "size", "color", "colour",
    "cotton", "linen", "formal", "casual", "summer", "comfortable",
    "breathable", "gym", "activewear", "wear", "shoe", "shoes", "relaxed",
    "fitted", "slim", "oversized",
}
OUT_OF_DOMAIN_TERMS = {
    "politics", "president", "election", "vote", "coding", "python", "java",
    "diagnosis", "medicine", "lawyer", "lawsuit", "cryptocurrency", "bitcoin",
}
ORDINAL_REFERENCE = r"(?:first|second|third|fourth|fifth|option\s*\d+|product\s*\d+)"
from app.llm.prompts import ROUTER_PROMPT


def route_by_rules(message: str) -> RouteDecision | None:
    text = message.strip().lower()
    if re.fullmatch(r"(?:hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", text):
        return RouteDecision(intent=Intent.GREETING, target_agent=AgentName.SALES)

    if any(term in text for term in OUT_OF_DOMAIN_TERMS) and not any(
        term in text for term in CLOTHING_TERMS
    ):
        return RouteDecision(
            intent=Intent.OUT_OF_DOMAIN,
            target_agent=AgentName.SALES,
            out_of_domain=True,
        )

    if "clear" in text and "cart" in text:
        return RouteDecision(intent=Intent.CART_CLEAR, target_agent=AgentName.CART)
    if any(phrase in text for phrase in ("show my cart", "view cart", "what is in my cart", "what's in my cart")):
        return RouteDecision(intent=Intent.CART_VIEW, target_agent=AgentName.CART)
    if any(word in text for word in ("remove", "delete")) and ("cart" in text or "item" in text or "one" in text):
        return RouteDecision(intent=Intent.CART_REMOVE, target_agent=AgentName.CART)
    if any(word in text for word in ("change", "update", "quantity")) and ("cart" in text or re.search(r"\b\d+\b", text)):
        return RouteDecision(intent=Intent.CART_UPDATE, target_agent=AgentName.CART)
    if "add" in text and ("cart" in text or "one" in text or "it" in text or re.search(ORDINAL_REFERENCE, text)):
        return RouteDecision(intent=Intent.CART_ADD, target_agent=AgentName.CART)

    if any(phrase in text for phrase in ("similar", "something like", "more like this", "alternatives")):
        return RouteDecision(intent=Intent.FIND_SIMILAR, target_agent=AgentName.SHOPPING)
    if re.search(ORDINAL_REFERENCE, text) and any(
        phrase in text for phrase in ("like", "good", "prefer", "choose", "pick", "want")
    ):
        return RouteDecision(intent=Intent.PRODUCT_SELECTION, target_agent=AgentName.SHOPPING)
    if any(phrase in text for phrase in ("previous one", "that one was good", "this one is good")):
        return RouteDecision(intent=Intent.PRODUCT_SELECTION, target_agent=AgentName.SHOPPING)
    if re.search(ORDINAL_REFERENCE, text) and len(text.split()) <= 5:
        return RouteDecision(intent=Intent.PRODUCT_SELECTION, target_agent=AgentName.SHOPPING)
    if any(phrase in text for phrase in ("in stock", "available", "availability")):
        return RouteDecision(intent=Intent.AVAILABILITY_CHECK, target_agent=AgentName.SHOPPING)
    if any(phrase in text for phrase in ("details", "tell me about", "more about")):
        return RouteDecision(intent=Intent.PRODUCT_DETAILS, target_agent=AgentName.SHOPPING)
    if any(term in text for term in ("match with", "what should i wear", "style", "fashion advice", "goes with", "occasion")):
        return RouteDecision(intent=Intent.FASHION_ADVICE, target_agent=AgentName.FASHION)
    if any(term in text for term in CLOTHING_TERMS) and (
        any(term in text for term in ("show", "find", "need", "want", "looking", "under", "available", "buy"))
        or len(text.split()) <= 4
    ):
        return RouteDecision(intent=Intent.PRODUCT_SEARCH, target_agent=AgentName.SHOPPING)

    return None


class RouterService:
    def __init__(self, llm: LLMClient, config: AgentConfig) -> None:
        self._llm = llm
        self._config = config

    async def route(self, message: str, context: ConversationState) -> RouteDecision:
        deterministic = route_by_rules(message)
        if deterministic:
            return deterministic

        if context.shopping_stage == "clarifying":
            return RouteDecision(
                intent=Intent.PRODUCT_SEARCH,
                target_agent=AgentName.SHOPPING,
                confidence=0.95,
            )

        if self._llm.configured:
            try:
                messages = [LLMMessage(role="system", content=ROUTER_PROMPT)]
                for msg in context.messages[-self._config.recent_message_limit :]:
                    messages.append(LLMMessage(role=msg.role, content=msg.content))
                
                system_context = json.dumps(
                    {
                        "shopping_stage": context.shopping_stage,
                        "preferences": context.preferences.model_dump(mode="json"),
                        "displayed_products": [
                            item.model_dump(mode="json") for item in context.displayed_products
                        ],
                        "selected_product": (
                            context.selected_product.model_dump(mode="json") if context.selected_product else None
                        ),
                        "has_cart": context.cart_id is not None,
                    },
                    default=str,
                )
                messages.append(LLMMessage(role="system", content=f"Context State: {system_context}"))
                
                return await self._llm.generate_structured(
                    messages,
                    RouteDecision,
                )
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise

        return RouteDecision(
            intent=Intent.GENERAL_SHOPPING_HELP,
            target_agent=AgentName.SALES,
            confidence=0.5,
        )
