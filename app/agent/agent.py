"""The core single-agent engine using Tool Calling."""

import logging
import json
from typing import Optional, Any

from app.agent.state import ConversationState
from app.agent.schemas import tools as AGENT_TOOLS
from app.agent.registry import TOOL_REGISTRY
from app.agent.intent import IntentExtractor, StructuredIntent, IntentPlan
from app.agent.utils import (
    clean_reply_formatting,
    format_store_context_str,
    is_greeting_or_reset_message,
    build_concierge_greeting,
    execute_validated_tool,
    args_from_intent,
    detect_input_language,
)
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SYSTEM_PROMPT_ROUTING, SYSTEM_PROMPT_VOICE

logger = logging.getLogger(__name__)


def _clean_reply_formatting(reply: str) -> str:
    """Delegated to clean_reply_formatting in app.agent.utils for backwards compatibility."""
    return clean_reply_formatting(reply)


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

        # Always clear transient UI cards at the start of every turn so stale cards never carry over
        state.clear_cards()

        # Check if user greets or explicitly requests resetting session
        is_greeting, is_reset = is_greeting_or_reset_message(user_message)
        if is_greeting or is_reset:
            state.reset(keep_cart=True)
            state.current_intent = "greeting"
            state.message_history.append({"role": "user", "content": user_message})
            reply = build_concierge_greeting(context.store_name, user_message)
            return self.reply(reply, state)

        # Handle explicit branch inquiries professionally
        user_lower = user_message.lower()
        branch_terms = ["gulberg", "f-7", "f7", "mall road", "which branch", "in branch", "at branch", "physical outlet", "physical store", "store location"]
        if any(term in user_lower for term in branch_terms) and not any(term in user_lower for term in ["buy", "add to cart", "checkout"]):
            state.current_intent = "branch_inquiry"
            state.message_history.append({"role": "user", "content": user_message})
            reply = (
                "Northstar Menswear operates as an online platform delivering orders directly to your doorstep nationwide. "
                "All in-stock items across our store network are available for online purchase. "
                "If you prefer to visit or purchase directly from a physical retail store, we invite you to visit your nearest Northstar branch location."
            )
            return self.reply(reply, state)

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
        cleaned_text = clean_reply_formatting(reply_text)

        # General chat, greetings, store overviews, and general inquiries MUST NEVER show product cards
        is_general_turn = state.current_intent in [
            "general_chat", "greeting", "general_inquiry", "store_overview", "faq", "general",
            "reset_session", "clear_preferences", "concierge_greeting"
        ]

        text_lower = cleaned_text.lower()
        is_general_prompt_or_overview = any(
            phrase in text_lower
            for phrase in [
                "what style or outfit", "what style are you", "what kind of", "what style of",
                "which type of", "which style", "what type", "which category or specific look",
                "interests you, and i will present", "as your personal ai sales concierge",
                "our current collection includes", "let me know which category",
                "elevate your personality", "boost your confidence",
                "کس قسم کی", "کون سا اسٹائل", "کون سی شرٹ", "کون سا انداز", "کون سی پینٹ", "کون سے کپڑے"
            ]
        )

        if is_general_turn or is_general_prompt_or_overview:
            state.displayed_products.clear()
            state.product_cards.clear()
        else:
            state.sync_displayed_products_with_reply(cleaned_text)

        state.message_history.append({"role": "assistant", "content": cleaned_text})
        return cleaned_text

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

        if intent.intent == "general_chat":
            return "General chat intent detected. No tool executed."

        if intent.intent in ["reset_session", "clear_session", "new_session"]:
            state.reset(keep_cart=True)
            return "Session reset successfully. All previous state cleared."

        if intent.intent == "clear_preferences":
            state.clear_search_preferences()
            state.displayed_products.clear()
            state.product_cards.clear()
            return "Preferences cleared."

        tool_name = intent.intent
        if tool_name == "remove_cart" and intent.selected_product_index is None:
            tool_name = "clear_cart"

        spec = TOOL_REGISTRY.get(tool_name)
        if not spec:
            return f"No tool mapping for intent {intent.intent}"

        args = self._args_from_intent(intent, state)
        return await execute_validated_tool(spec, args, state)

    def _args_from_intent(self, intent: StructuredIntent, state: ConversationState) -> dict:
        """Extract arguments from the intent for tool execution."""
        return args_from_intent(intent, state)

    async def _synthesize_reply(self, step_results: list[str], state: ConversationState, context: StoreContext) -> str:
        """Synthesize a natural language reply from the step results matching user input language and optimized for TTS playback."""
        results_str = "\n\n---\n\n".join(step_results)
        store_ctx_str = format_store_context_str(context)

        # Detect language of last user message
        last_user_msg = ""
        for msg in reversed(state.message_history):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        lang = detect_input_language(last_user_msg)

        if lang == "ur":
            language_mandate = (
                "STRICT LANGUAGE MANDATE:\n"
                "The user input is URDU (Urdu script or Roman Urdu speech transcript).\n"
                "YOU MUST REPLY STRICTLY IN URDU SCRIPT (اردو - Nasta'liq).\n"
                "NEVER reply in English. NEVER write Roman Urdu ('Aap ke cart me...', 'Pehla option...').\n"
                "Write clear, professional Urdu script (e.g. 'یہ لیجیے، آپ کے لیے بہترین ٹی شرٹس موجود ہیں').\n"
                "Ensure prices use 'روپے' label and whole integer numbers (e.g. 1000 روپے)."
            )
        else:
            language_mandate = (
                "STRICT LANGUAGE MANDATE:\n"
                "The user input is ENGLISH.\n"
                "YOU MUST REPLY STRICTLY IN PROFESSIONAL ENGLISH.\n"
                "NEVER reply in Urdu script or Roman Urdu.\n"
                "Ensure prices use 'rupees' label and whole integer numbers (e.g. 1000 rupees)."
            )

        system_content = (
            f"{SYSTEM_PROMPT_VOICE}\n\n"
            f"{store_ctx_str}\n\n"
            f"Current State:\n{state.model_dump_json(exclude_defaults=True)}\n\n"
            "Action Results:\n"
            f"{results_str}\n\n"
            f"{language_mandate}\n\n"
            "TEXT-TO-SPEECH (TTS) FORMATTING MANDATE:\n"
            "The reply will be spoken aloud to the customer via Text-to-Speech (TTS).\n"
            "DO NOT use markdown symbols like **, *, #, bullet asterisks, or complex code blocks.\n"
            "Use clear, natural sentences ending with full stops (.) for smooth voice pauses.\n\n"
            "Synthesize a conversational reply for the customer based on these results."
        )

        messages = [LLMMessage(role="system", content=system_content)]
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
        store_ctx_str = format_store_context_str(context)
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
                    result_str = await execute_validated_tool(spec, args, state)

                tool_msg = {"role": "tool", "tool_call_id": tc_id, "content": result_str}
                state.message_history.append(tool_msg)
                messages.append(LLMMessage(**tool_msg))

        if last_content:
            return self.reply(last_content, state)
        return self.reply("I have executed the requested actions.", state)
