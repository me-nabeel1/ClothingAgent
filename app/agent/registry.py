"""Single source of truth for every agent-callable action.

Adding a new action to the agent means: define its Pydantic payload model,
write its AgentTools handler method, and register one ToolSpec here. Nothing
else in the orchestrator, checker, or LLM tool-calling plumbing needs to
change when a new tool is added.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSpec:
    """Full definition of one agent-callable action."""

    name: str
    payload_model: type[BaseModel]
    handler: Callable[..., Awaitable[Any]]
    soft_required: dict[str, Callable[[Any, dict], Any]] | None = None
    mutates_state: bool = False
    card_type: str | None = None  # "product_list" | "cart" | "checkout" | "order" | None


TOOL_REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    """Register one tool. Raises if a tool with the same name is already
    registered — duplicate names are always a bug, never intentional."""
    if spec.name in TOOL_REGISTRY:
        raise ValueError(f"Tool '{spec.name}' is already registered.")
    TOOL_REGISTRY[spec.name] = spec


def get_tool(name: str) -> ToolSpec | None:
    return TOOL_REGISTRY.get(name)


def register_all_tools(tools_instance: Any) -> None:
    TOOL_REGISTRY.clear()
    from app.agent.schemas import (
        ExploreCategoryPayload,
        SearchProductsPayload,
        GetProductDetailsPayload,
        AddCartItemPayload,
        RemoveCartItemPayload,
        ShowCartPayload,
        PreviewCheckoutPayload,
        PlaceOrderPayload,
        GetPromotionsPayload,
        UpdateCartItemPayload,
        ClearCartPayload,
        CheckAvailabilityPayload,
        GetOrderStatusPayload
    )
    from app.agent.state import ConversationState

    def resolve_product_id(state: ConversationState, args: dict) -> Any:
        idx = args.get("selected_product_index")
        if idx is not None:
            try:
                idx_int = int(idx)
                if state.displayed_products and 1 <= idx_int <= len(state.displayed_products):
                    return state.displayed_products[idx_int - 1].product_id
            except (ValueError, TypeError):
                pass
        if args.get("product_id"):
            try:
                return int(args.get("product_id"))
            except (ValueError, TypeError):
                return args.get("product_id")
        if state.selected_product_id:
            return state.selected_product_id
        if state.displayed_products:
            return state.displayed_products[0].product_id
        return None

    # ------------------------------------------------------------------
    # Each entry: (canonical_name, payload_model, handler, kwargs, aliases)
    #
    # canonical_name = the intent name from StructuredIntent.intent
    #                  (used by _execute_intent via TOOL_REGISTRY.get(intent.intent))
    # aliases        = the LLM tool-call names from schemas.py tools[]
    #                  (used by _fallback_llm_tool_turn via TOOL_REGISTRY.get(func_name))
    # ------------------------------------------------------------------
    _tools = [
        # search — intent "search", LLM calls it "search_products"
        ("search", SearchProductsPayload, getattr(tools_instance, "get_products", None) or getattr(tools_instance, "search", None),
         {"mutates_state": False}, ["search_products"]),

        # explore_category — LLM calls it "explore_category", intent also uses it
        ("explore_category", ExploreCategoryPayload, getattr(tools_instance, "explore_category", None) or getattr(tools_instance, "search", None),
         {"mutates_state": False}, []),

        # get_details — intent "get_details", LLM calls it "get_product_details"
        ("get_details", GetProductDetailsPayload, getattr(tools_instance, "get_product_details", None) or getattr(tools_instance, "get_details", None),
         {"mutates_state": False}, ["get_product_details"]),

        # add_to_cart — intent "add_to_cart", LLM calls it "add_cart_item"
        ("add_to_cart", AddCartItemPayload, getattr(tools_instance, "add_cart_item", None) or getattr(tools_instance, "add_to_cart", None),
         {"soft_required": {"product_id": resolve_product_id}, "mutates_state": True},
         ["add_cart_item"]),

        # remove_cart — intent "remove_cart", LLM calls it "remove_cart_item"
        ("remove_cart", RemoveCartItemPayload, getattr(tools_instance, "remove_cart_item", None) or getattr(tools_instance, "remove_cart", None),
         {"mutates_state": True}, ["remove_cart_item"]),

        # show_cart — same name for both intent and LLM
        ("show_cart", ShowCartPayload, tools_instance.show_cart,
         {"mutates_state": False}, []),

        # checkout — intent "checkout", LLM calls it "preview_checkout"
        ("checkout", PreviewCheckoutPayload, getattr(tools_instance, "preview_checkout", None) or getattr(tools_instance, "checkout", None),
         {"mutates_state": False}, ["preview_checkout"]),

        # place_order — same name for both
        ("place_order", PlaceOrderPayload, tools_instance.place_order,
         {"mutates_state": True}, []),

        # get_promotions — same name for both
        ("get_promotions", GetPromotionsPayload, tools_instance.get_promotions,
         {"mutates_state": False}, []),

        # update_cart_item — no separate intent name yet
        ("update_cart_item", UpdateCartItemPayload, tools_instance.update_cart_item,
         {"mutates_state": True}, []),

        # clear_cart — used when "remove_cart" has no specific item target
        ("clear_cart", ClearCartPayload, tools_instance.clear_cart,
         {"mutates_state": True}, []),

        # check_availability
        ("check_availability", CheckAvailabilityPayload, tools_instance.check_availability,
         {"mutates_state": False}, []),

        # get_order_status
        ("get_order_status", GetOrderStatusPayload, tools_instance.get_order_status,
         {"mutates_state": False}, []),
    ]

    for canonical_name, payload_model, handler, kwargs, aliases in _tools:
        spec = ToolSpec(
            name=canonical_name,
            payload_model=payload_model,
            handler=handler,
            **kwargs
        )
        register(spec)
        # Register aliases pointing to the same spec
        for alias in aliases:
            TOOL_REGISTRY[alias] = spec

