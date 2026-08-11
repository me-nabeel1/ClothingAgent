"""Structured intent extraction using the single LLM."""

from __future__ import annotations

import logging
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.agent.state import ConversationState, Budget
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage

logger = logging.getLogger(__name__)


class ExtractedFilters(BaseModel):
    """Shopping constraints extracted from natural language."""
    categories: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)
    sizes: dict[str, str] = Field(default_factory=dict, description="e.g. {'shirt': 'L', 'pants': '34'}")
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    branch: Optional[str] = None
    specific_article: Optional[str] = Field(None, description="Exact article code if mentioned (e.g., NS-SH-001)")


class StructuredIntent(BaseModel):
    """The complete intention of the customer's message."""
    intent: str = Field(description="One of: 'search', 'get_details', 'add_to_cart', 'remove_cart', 'checkout', 'general_chat', 'clear_preferences'")
    filters: Optional[ExtractedFilters] = Field(default=None, description="Filters to apply or merge, if this is a search intent")
    selected_product_index: Optional[int] = Field(None, description="1-based index of product if user is referring to a recently displayed product list")
    search_query: Optional[str] = Field(None, description="Free text semantic search if specific vocabulary doesn't match")
    quantity: Optional[int] = Field(1, description="Quantity for cart actions")


class IntentExtractor:
    """Extracts structured meaning from customer messages."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def extract(
        self,
        user_input: str,
        state: ConversationState,
        context: StoreContext,
    ) -> StructuredIntent:
        """Parse user input into a StructuredIntent using store vocabulary."""
        
        system_instruction = (
            f"You are a routing and extraction engine for {context.store_name}.\n"
            "Analyze the user's message and current state, then output a JSON object.\n\n"
            "Current state summary:\n"
            f"- Stage: {state.conversation_stage}\n"
            f"- Intent: {state.current_intent}\n"
            f"- Categories: {state.categories}\n"
            f"- Occasions: {state.occasions}\n"
            f"- Colors: {state.preferred_colors}\n\n"
            "Available Vocabulary (Must match EXACTLY if used):\n"
            f"Categories: {context.categories}\n"
            f"Product Types: {context.product_types}\n"
            f"Occasions: {context.occasions}\n"
            f"Colors: {context.colors}\n"
            f"Sizes: {context.sizes}\n"
            f"Materials: {context.supported_attributes}\n"
            f"Branches: {[b.branch_code for b in context.branches]}\n\n"
            "Rules:\n"
            "1. If the user asks for products, intent is 'search'. Provide the filters delta.\n"
            "2. Map words to the exact vocabulary above. For example, 'wedding' -> 'wedding'.\n"
            "3. 'selected_product_index' should be a number (1, 2, 3) if they refer to 'the first one', etc.\n"
        )

        messages = [
            LLMMessage(role="system", content=system_instruction),
            LLMMessage(role="user", content=user_input)
        ]
        
        logger.info("extracting_intent", extra={"event": "extracting_intent", "user_input": user_input})
        result = await self._llm.generate_structured(messages, StructuredIntent)
        logger.info(
            "intent_extracted", 
            extra={"event": "intent_extracted", "intent": result.intent}
        )
        return result
