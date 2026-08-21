"""Fitzy's V1 runtime orchestrator."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from .contracts import ToolName
from .execution import ActionExecutionCoordinator
from .intent import IntentExtraction, IntentRequest, IntentType
from .planner import ActionPlanner
from .response import ResponseGuard
from .state import (
    ActionStatus,
    ConversationState,
    DisplayedProductReference,
    LanguageMode,
)
from ..integration.client import CommerceToolAdapter
from ..integration.schemas import ProductSearchResponse
from ..llm.client import LLMClient
from ..llm.prompts import build_intent_system_prompt

logger = logging.getLogger("fitzy.agent")


class FitzyAgent:
    """Coordinate language understanding, planning, requirements and tool execution."""

    def __init__(self, *, llm: LLMClient, tools: CommerceToolAdapter) -> None:
        self._llm = llm
        self._tools = tools
        self._planner = ActionPlanner()
        self._execution = ActionExecutionCoordinator()
        self._responses = ResponseGuard(llm)
        self._states: dict[str, ConversationState] = {}

    def get_state(self, session_id: str) -> ConversationState:
        """Return an existing conversation state or create a fresh one."""

        if session_id not in self._states:
            self._states[session_id] = ConversationState()
        return self._states[session_id]

    async def process_message(self, *, session_id: str, message: str) -> str:
        """Process one customer message through the full V1 runtime pipeline."""

        state = self.get_state(session_id)
        logger.info("message.received session=%s", session_id)

        extraction = await self._extract_intent(message)
        state.set_language(extraction.language)
        logger.info("intent.extracted session=%s language=%s intents=%s", session_id, extraction.language, [i.intent_type.value for i in extraction.intents])

        self._apply_intent_to_state(extraction, state)
        plan = self._planner.build_plan(extraction, state)
        state.action_plan = plan
        logger.info("plan.created session=%s plan=%s actions=%s", session_id, plan.plan_id, [(a.action_id, a.tool_name.value, a.dependency_ids) for a in plan.actions])

        self._resolve_known_parameters(state)
        await self._execute_until_waiting(state)

        runtime_context = self._build_runtime_context(state)
        return await self._responses.generate(
            language=state.language or LanguageMode.ENGLISH,
            user_message=message,
            runtime_context=runtime_context,
        )

    async def _extract_intent(self, message: str) -> IntentExtraction:
        """Use the LLM only for semantic intent extraction."""

        return await self._llm.generate_structured(
            system_prompt=build_intent_system_prompt(),
            user_message=message,
            response_model=IntentExtraction,
        )

    def _apply_intent_to_state(self, extraction: IntentExtraction, state: ConversationState) -> None:
        """Persist customer preferences and temporary search information without conflating them."""

        for intent in extraction.intents:
            if intent.intent_type != IntentType.PRODUCT_SEARCH:
                if intent.explicit_confirmation is not None and intent.intent_type == IntentType.PLACE_ORDER:
                    state.last_tool_results["explicit_confirmation"] = intent.explicit_confirmation
                continue

            params = intent.parameters
            state.current_search.update_from_mapping({
                key: value
                for key, value in params.items()
                if key in type(state.current_search).model_fields
            })

            # Explicit preference language may be represented by the extractor.
            if params.get("remember_preference") is True:
                for field_name in (
                    "colors",
                    "excluded_colors",
                    "categories",
                    "product_types",
                    "occasions",
                    "materials",
                    "fits",
                    "size_mapping",
                    "minimum_price",
                    "maximum_price",
                    "branch_code",
                ):
                    value = params.get(field_name)
                    if value in (None, [], {}, ""):
                        continue
                    mapping = {
                        "colors": "preferred_colors",
                        "excluded_colors": "excluded_colors",
                        "categories": "preferred_categories",
                        "product_types": "preferred_product_types",
                        "occasions": "preferred_occasions",
                        "materials": "preferred_materials",
                        "fits": "preferred_fits",
                        "size_mapping": "size_mapping",
                        "minimum_price": "minimum_price",
                        "maximum_price": "maximum_price",
                        "branch_code": "branch_preference",
                    }
                    setattr(state.preferences, mapping[field_name], value)

    def _resolve_known_parameters(self, state: ConversationState) -> None:
        """Resolve values already known from state or previous tool results.

        This step never invents customer choices.  It only derives values that
        are deterministic from prior results, such as a cart ID or a product
        reference that already exists in the displayed product set.
        """

        cart_result = state.last_tool_results.get(ToolName.CREATE_CART.value)
        if cart_result is not None and getattr(cart_result, "cart_id", None):
            state.cart.cart_id = cart_result.cart_id

        latest_cart = state.last_tool_results.get(ToolName.GET_CART.value)
        if latest_cart is not None:
            self._apply_cart_result(state, latest_cart)

        add_result = state.last_tool_results.get(ToolName.ADD_TO_CART.value)
        if add_result is not None:
            self._apply_cart_result(state, add_result)

        preview = state.last_tool_results.get(ToolName.PREVIEW_CHECKOUT.value)
        if preview is not None and getattr(preview, "cart_id", None):
            state.cart.cart_id = preview.cart_id

        for action in state.action_plan.actions:
            self._resolve_action_parameters(state, action)

    def _resolve_action_parameters(self, state: ConversationState, action: Any) -> None:
        """Fill action parameters from deterministic conversation state."""

        params = action.parameters
        if action.tool_name in {ToolName.GET_CART, ToolName.ADD_TO_CART, ToolName.UPDATE_CART, ToolName.REMOVE_FROM_CART, ToolName.CLEAR_CART, ToolName.PREVIEW_CHECKOUT, ToolName.PLACE_ORDER}:
            if "cart_id" not in params and state.cart.cart_id:
                params["cart_id"] = str(state.cart.cart_id)

        if action.tool_name == ToolName.PLACE_ORDER:
            params.setdefault("customer_name", state.delivery.customer_name)
            params.setdefault("phone", state.delivery.phone)
            params.setdefault("delivery_address", state.delivery.delivery_address)
            params.setdefault("city", state.delivery.city)
            params.setdefault("delivery_notes", state.delivery.delivery_notes)

        if action.tool_name == ToolName.GET_PRODUCT_DETAILS:
            product_id = params.get("product_id")
            reference = params.get("product_reference") or params.get("display_index")
            if product_id is None and reference is not None:
                product_id = self._resolve_displayed_product_id(state, reference)
                if product_id is not None:
                    params["product_id"] = product_id
                    state.remember_selected_product(product_id)

        if action.tool_name == ToolName.ADD_TO_CART:
            reference = params.get("product_reference") or params.get("display_index")
            if params.get("variant_id") is None and reference is not None:
                option = self._resolve_variant_from_latest_search(state, reference, params)
                if option is not None:
                    params.setdefault("variant_id", option.variant_id)
                    params.setdefault("branch_id", option.branch_id)
                    params.setdefault("selected_product_id", option.product_id)
            params.setdefault("quantity", 1)

    @staticmethod
    def _resolve_displayed_product_id(state: ConversationState, reference: Any) -> int | None:
        """Resolve '1', '2', etc. against the latest displayed product set."""

        try:
            index = int(reference)
        except (TypeError, ValueError):
            return None
        match = next((item for item in state.displayed_products if item.index == index), None)
        return match.product_id if match else None

    def _resolve_variant_from_latest_search(self, state: ConversationState, reference: Any, params: dict[str, Any]) -> Any | None:
        """Resolve a displayed product to one unambiguous available variant."""

        result = state.last_tool_results.get(ToolName.GET_PRODUCTS.value)
        if not isinstance(result, ProductSearchResponse):
            return None
        try:
            index = int(reference)
        except (TypeError, ValueError):
            return None
        displayed = next((item for item in state.displayed_products if item.index == index), None)
        if displayed is None:
            return None

        candidates = [item for item in result.products if item.product_id == displayed.product_id]
        if params.get("color"):
            candidates = [item for item in candidates if (item.color or "").lower() == str(params["color"]).lower()]
        if params.get("size"):
            candidates = [item for item in candidates if (item.size or "").lower() == str(params["size"]).lower()]
        available = [item for item in candidates if item.available_quantity > 0 and item.is_available is not False]
        return available[0] if len(available) == 1 else None

    async def _execute_until_waiting(self, state: ConversationState) -> None:
        """Execute ready actions, refresh deterministic state, and continue dependencies."""

        for _ in range(10):
            self._resolve_known_parameters(state)
            result = await self._execution.run_ready_actions(
                state,
                tool_executor=self._tools.execute,
                state_values=self._state_values(state),
                derived_values=self._derived_values(state),
            )

            for action_id in result.completed_action_ids:
                action = state.action_plan.get(action_id)
                if action:
                    logger.info("action.completed action=%s tool=%s", action_id, action.tool_name.value)
                    self._apply_completed_action(state, action)

            if result.waiting_action_id:
                logger.info("action.waiting action=%s missing=%s", result.waiting_action_id, result.missing_parameters)
                return
            if result.failed_action_ids:
                logger.warning("action.failed actions=%s", result.failed_action_ids)
                return
            if not result.executed_action_ids:
                return

            if not state.action_plan.ready_actions():
                return

    def _apply_completed_action(self, state: ConversationState, action: Any) -> None:
        """Apply normalized tool results to state without duplicating backend logic."""

        result = state.last_tool_results.get(action.tool_name.value)
        if result is None:
            return

        if action.tool_name == ToolName.GET_PRODUCTS and isinstance(result, ProductSearchResponse):
            references: list[DisplayedProductReference] = []
            seen_products: set[int] = set()
            index = 1
            for option in result.products:
                if option.product_id in seen_products:
                    continue
                seen_products.add(option.product_id)
                references.append(
                    DisplayedProductReference(
                        index=index,
                        product_id=option.product_id,
                        article_code=option.article_code,
                        product_name=option.product_name,
                    )
                )
                index += 1
            state.remember_displayed_products(references)
        elif action.tool_name in {ToolName.CREATE_CART, ToolName.GET_CART, ToolName.ADD_TO_CART}:
            self._apply_cart_result(state, result)

    @staticmethod
    def _apply_cart_result(state: ConversationState, result: Any) -> None:
        """Update local cart metadata from an authoritative cart response."""

        if getattr(result, "cart_id", None):
            state.cart.cart_id = result.cart_id
        if getattr(result, "item_count", None) is not None:
            state.cart.item_count = int(result.item_count or 0)
        if getattr(result, "subtotal", None) is not None:
            state.cart.subtotal = Decimal(str(result.subtotal or 0))

    @staticmethod
    def _state_values(state: ConversationState) -> dict[str, Any]:
        """Flatten deterministic state values for generic requirement checking."""

        return {
            "cart_id": str(state.cart.cart_id) if state.cart.cart_id else None,
            "customer_name": state.delivery.customer_name,
            "phone": state.delivery.phone,
            "delivery_address": state.delivery.delivery_address,
            "city": state.delivery.city,
            "delivery_notes": state.delivery.delivery_notes,
        }

    @staticmethod
    def _derived_values(state: ConversationState) -> dict[str, Any]:
        """Provide deterministic defaults that do not invent customer choices."""

        return {
            "quantity": 1,
            "explicit_confirmation": state.last_tool_results.get("explicit_confirmation"),
        }

    def _build_runtime_context(self, state: ConversationState) -> dict[str, Any]:
        """Build compact response context from state and authoritative tool results."""

        results: dict[str, Any] = {}
        for key, value in state.last_tool_results.items():
            if hasattr(value, "model_dump"):
                results[key] = value.model_dump(mode="json")
            else:
                results[key] = value

        return {
            "language": state.language.value if state.language else None,
            "preferences": state.preferences.model_dump(mode="json"),
            "current_search": state.current_search.model_dump(mode="json"),
            "displayed_products": [item.model_dump(mode="json") for item in state.displayed_products],
            "delivery": state.delivery.model_dump(mode="json"),
            "cart": state.cart.model_dump(mode="json"),
            "pending_action_id": state.pending_action_id,
            "tool_results": results,
        }

    async def close(self) -> None:
        """Close the underlying commerce adapter transport when supported."""

        close = getattr(self._tools, "close", None)
        if close:
            result = close()
            if hasattr(result, "__await__"):
                await result
