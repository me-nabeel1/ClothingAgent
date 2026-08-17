"""The core single-agent engine using Tool Calling."""

import logging
import json
from typing import Optional, Any

from app.agent.state import ConversationState
from app.agent.schemas import tools as AGENT_TOOLS
from app.agent.registry import TOOL_REGISTRY
from app.agent.checker import ParameterRequirementsChecker
from app.agent.intent import IntentExtractor, StructuredIntent, IntentPlan
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SYSTEM_PROMPT_ROUTING, SYSTEM_PROMPT_VOICE

logger = logging.getLogger(__name__)


class SingleAgent:
    """The authoritative AI agent orchestrating conversation and business logic."""

    def __init__(self, llm: LLMClient, tools: Any = None, intent_extractor: Optional[IntentExtractor] = None) -> None:
        self._llm = llm
        self._tools = tools
        self._intent_extractor = intent_extractor
        if tools is not None:
            from app.agent.registry import register_all_tools
            register_all_tools(tools)

    async def process_message(
        self,
        user_message: str,
        state: ConversationState,
        context: StoreContext,
    ) -> str:
        """Process one conversational turn using the IntentPlan pipeline."""
        logger.info("agent_processing_message", extra={"event": "process_message"})

        # If user explicitly requests resetting session or starting fresh
        msg_clean = user_message.strip().lower()
        if msg_clean in ["reset", "reset session", "start fresh", "start over", "new chat", "clear session", "restart", "نئی سیشن", "نیا سیشن", "شروع سے", "دوبارہ شروع کرو"]:
            state.reset()
            return "Hello! I have reset your session and cleared all previous history. How can I assist you with your style today?"

        # 1. Append user message to history
        state.message_history.append({"role": "user", "content": user_message})

        # 2. Extract multi-intent plan
        try:
            plan = await self._intent_extractor.extract(user_message, state, context)
            logger.info(
                "plan_generated",
                extra={
                    "event": "plan_generated",
                    "step_count": len(plan.steps),
                    "intents": [s.intent.intent for s in plan.steps],
                },
            )
        except Exception as exc:
            logger.error("plan_extraction_failed", extra={"error": str(exc)})
            try:
                return await self._fallback_llm_tool_turn(state, context)
            except Exception as fallback_exc:
                logger.error("fallback_llm_tool_turn_failed", extra={"error": str(fallback_exc)})
                return await self._local_rule_fallback(user_message, state, context)

        # 3. Execute plan sequentially
        step_results = []
        for step in plan.steps:
            state.current_intent = step.intent.intent
            # Check dependency verification
            if step.depends_on:
                verify_flag = next((s.verify for s in plan.steps if s.step_id == step.depends_on), None)
                if not self._verify_postcondition(verify_flag, state):
                    step_results.append(f"Step {step.step_id} ({step.intent.intent}) skipped because dependency {step.depends_on} failed verification.")
                    continue

            # Update context from intent
            if step.intent.clear_previous_preferences:
                state.clear_search_preferences()
                state.displayed_products.clear()

            # Execute tool for intent
            result = await self._execute_intent(step.intent, state, context)
            step_results.append(f"Step {step.step_id} ({step.intent.intent}) result:\n{result}")

            # Filter cards to selected indices if user shortlisted/selected specific products
            selected_indices = getattr(step.intent, "selected_product_indices", [])
            if not selected_indices and getattr(step.intent, "selected_product_index", None) is not None:
                selected_indices = [step.intent.selected_product_index]
            if selected_indices and state.displayed_products and step.intent.intent not in ["search", "add_to_cart", "remove_cart", "show_cart", "clear_cart"]:
                state.filter_displayed_cards(selected_indices)

        # 4. Synthesize final reply
        reply_text = await self._synthesize_reply(step_results, state, context)
        return self.reply(reply_text, state)

    def reply(self, reply_text: str, state: ConversationState) -> str:
        """Finalize assistant turn reply, synchronize product cards with reply prose, and record message history."""
        state.sync_displayed_products_with_reply(reply_text)
        state.message_history.append({"role": "assistant", "content": reply_text})
        return reply_text

    def _verify_postcondition(self, verify: str | None, state: ConversationState) -> bool:
        """Check if a postcondition is met in the state."""
        if not verify:
            return True

        if verify == "cart_is_empty":
            return state.cart_card is None or state.cart_card.item_count == 0

        logger.warning(
            "unrecognized_postcondition_verify",
            extra={"event": "unrecognized_postcondition_verify", "verify": verify},
        )
        return True


    async def _execute_intent(self, intent: StructuredIntent, state: ConversationState, context: StoreContext) -> str:
        """Map StructuredIntent to tool calls via TOOL_REGISTRY and execute them."""

        # Non-tool intents handled directly
        if intent.intent == "general_chat":
            return "General chat intent detected. No tool executed."

        if intent.intent in ["reset_session", "clear_session", "new_session"]:
            state.reset()
            return "Session reset successfully. All previous state cleared."

        if intent.intent == "clear_preferences":
            state.clear_search_preferences()
            state.displayed_products.clear()
            state.product_cards.clear()
            return "Preferences cleared."

        # Route "remove_cart" with no specific item to "clear_cart"
        tool_name = intent.intent
        if tool_name == "remove_cart" and intent.selected_product_index is None:
            # No specific item → user wants to empty the entire cart
            tool_name = "clear_cart"

        spec = TOOL_REGISTRY.get(tool_name)
        if not spec:
            return f"No tool mapping for intent {intent.intent}"

        args = self._args_from_intent(intent, state)

        try:
            validation_error = await ParameterRequirementsChecker.check(spec, args, state)
            if validation_error:
                return validation_error

            payload = spec.payload_model(**args)
            result = await spec.handler(state, payload)
            # Ensure result is a string for synthesis
            return result if isinstance(result, str) else str(result)

        except Exception as exc:
            logger.error(f"Error executing {tool_name}: {exc}")
            return f"Error executing {tool_name}: {str(exc)}"

    def _args_from_intent(self, intent: StructuredIntent, state: ConversationState) -> dict:
        """Extract arguments from the intent for tool execution."""
        args = {}
        filters = intent.search_overrides or intent.filters
        if filters:
            if filters.categories:
                args["categories"] = filters.categories
                args["category_name"] = filters.categories[0]
            if filters.product_types: args["product_types"] = filters.product_types
            if filters.occasions: args["occasions"] = filters.occasions
            if filters.colors:
                args["colors"] = filters.colors
                args["color"] = filters.colors[0]
            if filters.excluded_colors: args["excluded_colors"] = filters.excluded_colors
            if filters.sizes:
                args["size_mapping"] = filters.sizes
                if isinstance(filters.sizes, dict) and filters.sizes:
                    args["size"] = next(iter(filters.sizes.values()))
                elif isinstance(filters.sizes, list) and filters.sizes:
                    args["size"] = str(filters.sizes[0])
                elif isinstance(filters.sizes, str):
                    args["size"] = filters.sizes
            if filters.materials: args["materials"] = filters.materials
            if filters.fits: args["fits"] = filters.fits
            if filters.budget:
                if getattr(filters.budget, 'minimum', None) is not None: args["minimum_price"] = filters.budget.minimum
                if getattr(filters.budget, 'maximum', None) is not None: args["maximum_price"] = filters.budget.maximum
            if filters.branch: args["branch_code"] = filters.branch
            if filters.specific_article: args["article_code"] = filters.specific_article
            
        if intent.search_query:
            args["query_text"] = intent.search_query
            
        if intent.selected_product_index is not None:
            args["selected_product_index"] = intent.selected_product_index
            if 1 <= intent.selected_product_index <= len(state.displayed_products):
                args["product_id"] = state.displayed_products[intent.selected_product_index - 1].product_id
                args["item_id"] = state.displayed_products[intent.selected_product_index - 1].product_id
                
        if intent.quantity:
            args["quantity"] = intent.quantity
            
        if intent.delivery_info:
            if intent.delivery_info.customer_name: args["customer_name"] = intent.delivery_info.customer_name
            if intent.delivery_info.phone: args["phone"] = intent.delivery_info.phone
            if intent.delivery_info.delivery_address: args["delivery_address"] = intent.delivery_info.delivery_address
            if intent.delivery_info.city: args["city"] = intent.delivery_info.city
            if intent.delivery_info.delivery_notes: args["delivery_notes"] = intent.delivery_info.delivery_notes
            
        return args

    async def _synthesize_reply(self, step_results: list[str], state: ConversationState, context: StoreContext) -> str:
        """Synthesize a natural language reply from the step results."""
        results_str = "\n\n---\n\n".join(step_results)
        
        store_ctx_str = (
            f"Brand/Store Context:\n"
            f"- Brand Name: {context.store_name}\n"
            f"- Available Categories: {context.categories}\n"
            f"- Available Product Types: {context.product_types}\n"
            f"- Available Occasions: {context.occasions}\n"
            f"- Available Colors: {context.colors}\n"
            f"- Available Sizes: {context.sizes}\n"
        )

        system_content = (
            f"{SYSTEM_PROMPT_VOICE}\n\n"
            f"{store_ctx_str}\n\n"
            f"Current State:\n{state.model_dump_json(exclude_defaults=True)}\n\n"
            "Action Results:\n"
            f"{results_str}\n\n"
            "Synthesize a conversational reply for the customer based on these results."
        )
        
        messages = [LLMMessage(role="system", content=system_content)]
        
        # Add last few messages for context
        for msg in state.message_history[-4:]:
            messages.append(LLMMessage(**msg))
            
        try:
            content, _ = await self._llm.generate_with_tools(messages, tools=[])
            if content:
                return content
        except Exception as exc:
            logger.warning(f"Synthesis LLM call failed, using raw step results: {exc}")

        return results_str or "I have processed your request."

    async def _local_rule_fallback(self, user_message: str, state: ConversationState, context: StoreContext) -> str:
        """Local fallback when LLM service is completely unavailable."""
        from app.agent.schemas import SearchProductsPayload
        try:
            search_payload = SearchProductsPayload(query=user_message, limit=3)
            await self._tools.get_products(state, search_payload)
        except Exception as exc:
            logger.warning(f"Fallback search failed: {exc}")

        if state.displayed_products:
            prod_items = []
            for idx, dp in enumerate(state.displayed_products, 1):
                prod_items.append(f"{idx}. {dp.product_name} – Rs {int(dp.price)}")
            prods_str = "\n".join(prod_items)
            reply = (
                f"Welcome to {context.store_name}!\n\n"
                f"Here are some options from our collection:\n"
                f"{prods_str}\n\n"
                f"Which option would you like to know more about?"
            )
        else:
            reply = f"Welcome to {context.store_name}! How can I help you find what you're looking for today?"

        return self.reply(reply, state)


    async def _fallback_llm_tool_turn(self, state: ConversationState, context: StoreContext) -> str:
        """Legacy tool loop used as fallback if intent extraction fails."""
        store_ctx_str = (
            f"Brand/Store Context:\n"
            f"- Brand Name: {context.store_name}\n"
            f"- Available Categories: {context.categories}\n"
            f"- Available Product Types: {context.product_types}\n"
            f"- Available Occasions: {context.occasions}\n"
            f"- Available Colors: {context.colors}\n"
            f"- Available Sizes: {context.sizes}\n"
        )
        # 2. Build system context
        system_content = (
            f"{SYSTEM_PROMPT_ROUTING}\n\n"
            f"{SYSTEM_PROMPT_VOICE}\n\n"
            f"{store_ctx_str}\n\n"
            f"Current State:\n{state.model_dump_json(exclude_defaults=True)}\n\n"
        )
        
        messages = [LLMMessage(role="system", content=system_content)]
        for msg in state.message_history:
            messages.append(LLMMessage(**msg))
            
        max_turns = 5
        last_content = ""
        while max_turns > 0:
            max_turns -= 1
            content, tool_calls = await self._llm.generate_with_tools(messages, tools=AGENT_TOOLS)
            if content:
                last_content = content
                
            if not tool_calls:
                if content:
                    return self.reply(content, state)
                return self.reply(last_content or "I have processed your request.", state)
                
            assistant_msg = {"role": "assistant", "content": content, "tool_calls": tool_calls}
            state.message_history.append(assistant_msg)
            messages.append(LLMMessage(**assistant_msg))
            
            for tc in tool_calls:
                tc_id = tc.get("id")
                func_name = tc.get("function", {}).get("name")
                args_str = tc.get("function", {}).get("arguments", "{}")
                try:
                    args = json.loads(args_str)
                except Exception:
                    args = {}
                    
                spec = TOOL_REGISTRY.get(func_name)
                
                if not spec:
                    result_str = f"Unknown tool: {func_name}"
                else:
                    validation_error = await ParameterRequirementsChecker.check(spec, args, state)
                    if validation_error:
                        result_str = validation_error
                    else:
                        try:
                            payload = spec.payload_model(**args)
                            res = await spec.handler(state, payload)
                            result_str = res if isinstance(res, str) else str(res)
                        except Exception as e:
                            result_str = f"Error executing {func_name}: {str(e)}"
                
                tool_msg = {"role": "tool", "tool_call_id": tc_id, "content": result_str}
                state.message_history.append(tool_msg)
                messages.append(LLMMessage(**tool_msg))

        if last_content:
            return self.reply(last_content, state)
        return self.reply("I have executed the requested actions.", state)
