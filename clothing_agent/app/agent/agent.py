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
            
        if intent_result.search_overrides:
            raw = intent_result.search_overrides.model_dump(exclude_unset=True)
            field_map = {
                "colors": "preferred_colors",
                "sizes": "size_preferences",
                "branch": "branch_preference",
            }
            mapped: dict = {}
            for key, value in raw.items():
                mapped_key = field_map.get(key, key)
                mapped[mapped_key] = value
            state.current_search = mapped
        else:
            state.current_search.clear()
            
        if intent_result.selected_product_index:
            state.selected_product_id = state.displayed_products[intent_result.selected_product_index - 1].product_id if 0 < intent_result.selected_product_index <= len(state.displayed_products) else None

        if intent_result.delivery_info:
            raw_delivery = intent_result.delivery_info.model_dump(exclude_unset=True)
            state.update({"delivery": raw_delivery})
            
        if intent_result.order_confirmed is not None:
            state.update({"order_confirmed": intent_result.order_confirmed})

    async def _execute_action(
        self,
        intent_result: StructuredIntent,
        state: ConversationState,
        user_message: str,
    ) -> str:
        """Execute the appropriate semantic tool based on intent."""
        
        if intent_result.intent == "search":
            products_res = await self._tools.get_products(state, intent_result.search_query)
            if products_res.products:
                lines = [f"Retrieved {len(products_res.products)} products matching criteria:"]
                for p in products_res.products:
                    is_avail = any(v.is_available for v in p.variants)
                    avail_str = "Available" if is_avail else "Out of Stock"
                    lines.append(f"- ID: {p.product_id} | Name: {p.product_name} | Price: {p.final_price} | {avail_str}")
                return "\n".join(lines)
            return "No products found matching these criteria."

        elif intent_result.intent == "get_details":
            if state.selected_product_id:
                details = await self._tools.get_product_details(state.selected_product_id)
                p = details.product
                lines = [
                    f"Product Details for {p.product_name} (ID: {p.product_id}, Code: {p.article_code})",
                    f"Category: {p.category} | Type: {p.product_type} | Gender: {p.gender}",
                    f"Material: {p.material or 'N/A'} | Fit: {p.fit or 'N/A'} | Occasion: {p.occasion or 'N/A'}",
                    f"Price: {p.base_price} | Final Price: {p.final_price} | Discount: {p.discount_amount}",
                ]
                if p.applied_offer:
                    lines.append(f"Applied Offer: {p.applied_offer.offer_name} ({p.applied_offer.description})")
                
                # Summarize variants
                available_colors = set()
                available_sizes = set()
                oos_colors = set()
                oos_sizes = set()
                branches_with_stock = set()
                
                for v in p.variants:
                    if v.is_available:
                        available_colors.add(v.color)
                        available_sizes.add(v.size)
                        for b in v.branch_availability:
                            if b.is_available:
                                branches_with_stock.add(b.branch_name)
                    else:
                        oos_colors.add(v.color)
                        oos_sizes.add(v.size)
                
                lines.append(f"Available Colors: {', '.join(available_colors) if available_colors else 'None'}")
                if oos_colors - available_colors:
                    lines.append(f"Out of Stock Colors: {', '.join(oos_colors - available_colors)}")
                    
                lines.append(f"Available Sizes: {', '.join(available_sizes) if available_sizes else 'None'}")
                if oos_sizes - available_sizes:
                    lines.append(f"Out of Stock Sizes: {', '.join(oos_sizes - available_sizes)}")
                    
                lines.append(f"Available at Branches: {', '.join(branches_with_stock) if branches_with_stock else 'None'}")
                
                return "\n".join(lines)
            return "No product selected to get details for."

        elif intent_result.intent == "add_to_cart":
            if not state.selected_product_id:
                return "Cannot add to cart. No product is currently selected. Ask the user which product they want."
                
            details = await self._tools.get_product_details(state.selected_product_id)
            
            # Find matching variant based on size/color preferences
            target_size = None
            if details.product.product_type and details.product.product_type in state.size_preferences:
                target_size = state.size_preferences[details.product.product_type]
            elif details.product.category and details.product.category in state.size_preferences:
                target_size = state.size_preferences[details.product.category]
                
            available_variants = [v for v in details.product.variants if v.is_available]
            
            # Filter by color if specified
            if state.preferred_colors:
                available_variants = [v for v in available_variants if v.color.lower() in [c.lower() for c in state.preferred_colors]]
                
            # Filter by size if specified
            if target_size:
                available_variants = [v for v in available_variants if v.size.lower() == target_size.lower()]
                
            if len(available_variants) == 1:
                # Exactly one match, add it
                v = available_variants[0]
                # Just need a valid branch that has availability
                available_branches = [b for b in v.branch_availability if b.is_available]
                if not available_branches:
                    return "The requested option is out of stock across all branches."
                    
                branch_id = available_branches[0].branch_id
                
                await self._tools.add_cart_item(state, variant_id=v.variant_id, branch_id=branch_id)
                return "Added to cart."
            elif len(available_variants) > 1:
                return "Multiple options available. Ask the user to clarify size or color."
            else:
                return "The requested option is out of stock or does not exist. Inform the user."

        elif intent_result.intent == "remove_cart":
            # Just clear cart for V1 simplicity if no item specified, or would need item_id.
            # V1 doesn't specify item IDs in the prompt easily. 
            # I will return a placeholder or handle it properly.
            return "Cart item removal requested. (V1: you can also tell them to clear cart)"

        elif intent_result.intent == "checkout":
            preview = await self._tools.preview_checkout(state)
            if preview:
                return f"Checkout Preview:\n{json.dumps(preview.model_dump(), default=str)}"
            return "Cart is empty."

        elif intent_result.intent == "place_order":
            if not state.delivery.is_complete():
                missing = []
                if not state.delivery.customer_name: missing.append("name")
                if not state.delivery.phone: missing.append("phone number")
                if not state.delivery.delivery_address: missing.append("delivery address")
                if not state.delivery.city: missing.append("city")
                return f"Cannot place order yet. Missing delivery information: {', '.join(missing)}. Ask the user for this information."
                
            if not state.order_confirmed:
                return "Cannot place order yet. You MUST explicitly ask the user to confirm the order placement and total."
                
            order = await self._tools.place_order(
                state,
                customer_name=state.delivery.customer_name,
                phone=state.delivery.phone,
                delivery_address=state.delivery.delivery_address,
                city=state.delivery.city,
                delivery_notes=state.delivery.delivery_notes
            )
            if order:
                state.order_confirmed = False
                return f"Order placed successfully! Order Number: {order.order_number}"
            return "Failed to place order. Cart might be empty."

        elif intent_result.intent == "clear_preferences":
            return "Preferences cleared successfully."

        elif intent_result.intent == "general_chat":
            return "Process this as a general conversation based on the user's input."

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
