"""The core single-agent engine."""

import logging
import json
from typing import Optional

from app.agent.state import ConversationState
from app.agent.intent import IntentExtractor, StructuredIntent
from app.agent.tools import AgentTools
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SingleAgent:
    """The authoritative AI agent orchestrating conversation and business logic."""

    def __init__(self, llm: LLMClient, extractor: IntentExtractor, tools: AgentTools) -> None:
        self._llm = llm
        self._extractor = extractor
        self._tools = tools

    async def process_message(
        self,
        user_message: str,
        state: ConversationState,
        context: StoreContext,
    ) -> str:
        """Process one conversational turn."""
        logger.info("agent_processing_message", extra={"event": "process_message"})

        # 1. Extract Intent
        intent_result = await self._extractor.extract(user_message, state, context)

        # 2. Update State incrementally
        self._update_state(intent_result, state)

        # 3. Decide Action & Execute Tools
        context_data = await self._execute_action(intent_result, state, user_message)

        # 4. Build Final Response
        return await self._build_response(user_message, state, context_data)

    def _update_state(self, intent_result: StructuredIntent, state: ConversationState) -> None:
        """Incrementally update conversation state based on intent extraction."""
        if intent_result.intent == "clear_preferences":
            state.clear_search_preferences()
            
        state.current_intent = intent_result.intent

        if intent_result.filters:
            raw = intent_result.filters.model_dump(exclude_unset=True)
            # Map ExtractedFilters field names to ConversationState field names
            mapped: dict = {}
            field_map = {
                "colors": "preferred_colors",
                "sizes": "size_preferences",
                "branch": "branch_preference",
            }
            for key, value in raw.items():
                mapped_key = field_map.get(key, key)
                mapped[mapped_key] = value
            state.update(mapped)
            
        if intent_result.selected_product_index:
            state.selected_product_id = state.displayed_products[intent_result.selected_product_index - 1].product_id if 0 < intent_result.selected_product_index <= len(state.displayed_products) else None

    async def _execute_action(
        self,
        intent_result: StructuredIntent,
        state: ConversationState,
        user_message: str,
    ) -> str:
        """Execute the appropriate semantic tool based on intent."""
        
        # "Minimum Sufficient Intent Principle" - if we have search intent, execute immediately
        if intent_result.intent == "search":
            products_res = await self._tools.get_products(state, intent_result.search_query)
            if products_res.products:
                return f"Retrieved {len(products_res.products)} products matching criteria:\n{json.dumps([p.model_dump() for p in products_res.products], default=str)}"
            return "No products found matching these criteria."

        elif intent_result.intent == "get_details":
            if state.selected_product_id:
                details = await self._tools.get_product_details(state.selected_product_id)
                return f"Product Details:\n{json.dumps(details.model_dump(), default=str)}"
            return "No product selected to get details for."

        return "No specific backend action required for this intent."

    async def _build_response(
        self,
        user_message: str,
        state: ConversationState,
        action_context: str,
    ) -> str:
        """Consult the LLM to generate the final conversational response."""
        
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Current State:\n{state.model_dump_json(exclude_defaults=True)}\n\n"
            f"Action Result:\n{action_context}"
        )

        messages = [
            LLMMessage(role="system", content=system_content),
            LLMMessage(role="user", content=user_message)
        ]
        
        logger.info("generating_agent_response", extra={"event": "generating_response"})
        return await self._llm.generate_text(messages)
