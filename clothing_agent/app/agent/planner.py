"""Dependency-aware action planning for Fitzy.

The planner converts normalized customer intents into semantic tool actions.
It does not execute tools and does not know HTTP endpoints. Its only job is to
establish which actions can run now, which depend on other actions, and which
must remain blocked until a required fact or customer choice exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import ToolName
from .intent import IntentExtraction, IntentType, intent_to_tool
from .state import ActionPlan, ActionStatus, ConversationState, PlannedAction


@dataclass(frozen=True)
class PlanningRule:
    """Immutable dependency policy for one semantic intent."""

    intent_type: IntentType
    requires_product_resolution: bool = False
    requires_cart: bool = False
    requires_checkout_preview: bool = False


DEFAULT_PLANNING_RULES: dict[IntentType, PlanningRule] = {
    IntentType.PRODUCT_DETAILS: PlanningRule(IntentType.PRODUCT_DETAILS, requires_product_resolution=True),
    IntentType.ADD_TO_CART: PlanningRule(IntentType.ADD_TO_CART, requires_product_resolution=True, requires_cart=True),
    IntentType.UPDATE_CART: PlanningRule(IntentType.UPDATE_CART, requires_cart=True),
    IntentType.REMOVE_FROM_CART: PlanningRule(IntentType.REMOVE_FROM_CART, requires_cart=True),
    IntentType.CLEAR_CART: PlanningRule(IntentType.CLEAR_CART, requires_cart=True),
    IntentType.CHECKOUT: PlanningRule(IntentType.CHECKOUT, requires_cart=True),
    IntentType.PLACE_ORDER: PlanningRule(IntentType.PLACE_ORDER, requires_cart=True, requires_checkout_preview=True),
}


class ActionPlanner:
    """Build a dependency-aware graph without executing any tool."""

    def __init__(self, rules: dict[IntentType, PlanningRule] | None = None) -> None:
        self._rules = rules or DEFAULT_PLANNING_RULES

    def build_plan(
        self,
        extraction: IntentExtraction,
        state: ConversationState | None = None,
    ) -> ActionPlan:
        """Build a plan from multiple intents and known conversation state.

        Independent reads stay independent and can later run concurrently.
        Internal prerequisites such as cart creation or checkout preview are
        inserted only when they are necessary for a requested action and are
        not already satisfied by state or another action in the same plan.
        """

        state = state or ConversationState()
        actions: list[PlannedAction] = []
        last_search_id: str | None = None
        last_cart_write_id: str | None = None
        last_checkout_id: str | None = None
        has_cart = state.cart.cart_id is not None
        has_checkout = "preview_checkout" in state.last_tool_results

        for intent in extraction.intents:
            tool_name = intent_to_tool(intent.intent_type)
            if tool_name is None:
                continue

            params = dict(intent.parameters)
            dependencies: list[str] = []
            rule = self._rules.get(intent.intent_type)

            if intent.intent_type in {IntentType.PRODUCT_DETAILS, IntentType.ADD_TO_CART}:
                if not self._has_direct_product_reference(params):
                    if last_search_id:
                        dependencies.append(last_search_id)
                    elif state.selected_product_id is not None:
                        params.setdefault("product_id", state.selected_product_id)

            if rule and rule.requires_cart and not self._has_cart_reference(params) and not has_cart:
                if intent.intent_type == IntentType.ADD_TO_CART:
                    if last_cart_write_id and actions[last_cart_index(actions, last_cart_write_id)].tool_name == ToolName.CREATE_CART:
                        dependencies.append(last_cart_write_id)
                    else:
                        create_cart = PlannedAction(tool_name=ToolName.CREATE_CART, status=ActionStatus.PENDING)
                        actions.append(create_cart)
                        last_cart_write_id = create_cart.action_id
                        has_cart = True
                        dependencies.append(create_cart.action_id)
                # Checkout/order operations do not silently create an empty
                # cart. Their requirement checker must stop them until an
                # actual cart exists.

            if rule and rule.requires_checkout_preview and not has_checkout:
                if last_checkout_id:
                    dependencies.append(last_checkout_id)
                else:
                    checkout = PlannedAction(
                        tool_name=ToolName.PREVIEW_CHECKOUT,
                        parameters=params.get("cart_id") and {"cart_id": params["cart_id"]} or {},
                        dependency_ids=[last_cart_write_id] if last_cart_write_id else [],
                        status=ActionStatus.PENDING,
                    )
                    actions.append(checkout)
                    last_checkout_id = checkout.action_id
                    has_checkout = True
                    dependencies.append(checkout.action_id)

            if intent.intent_type == IntentType.PLACE_ORDER:
                params.setdefault("explicit_confirmation", intent.explicit_confirmation)

            action = PlannedAction(
                tool_name=tool_name,
                parameters=params,
                dependency_ids=self._deduplicate(dependencies),
                status=ActionStatus.PENDING,
            )
            actions.append(action)

            if intent.intent_type == IntentType.PRODUCT_SEARCH:
                last_search_id = action.action_id
            if tool_name in {
                ToolName.CREATE_CART,
                ToolName.ADD_TO_CART,
                ToolName.UPDATE_CART,
                ToolName.REMOVE_FROM_CART,
                ToolName.CLEAR_CART,
            }:
                last_cart_write_id = action.action_id
                if tool_name == ToolName.CREATE_CART:
                    has_cart = True
            if intent.intent_type == IntentType.CHECKOUT:
                last_checkout_id = action.action_id
                has_checkout = True

        return ActionPlan(actions=actions)

    @staticmethod
    def _has_direct_product_reference(parameters: dict[str, Any]) -> bool:
        """Return True when an intent already identifies a product directly."""

        return any(parameters.get(name) not in (None, "", [], {}) for name in (
            "product_id", "product_reference", "article_code", "sku", "variant_id"
        ))

    @staticmethod
    def _has_cart_reference(parameters: dict[str, Any]) -> bool:
        """Return True when the intent includes a cart identifier."""

        return parameters.get("cart_id") not in (None, "")

    @staticmethod
    def _deduplicate(values: list[str]) -> list[str]:
        """Preserve dependency order while removing duplicate action IDs."""

        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                output.append(value)
        return output


def action_index(actions: list[PlannedAction], action_id: str) -> int:
    """Return an action index; raise a clear error for an unknown dependency."""

    for index, action in enumerate(actions):
        if action.action_id == action_id:
            return index
    raise KeyError(f"Unknown action dependency: {action_id}")


def last_cart_index(actions: list[PlannedAction], action_id: str) -> int:
    """Compatibility alias used by planner dependency checks."""

    return action_index(actions, action_id)
