"""Structured intent models for Fitzy's Phase 2 planning layer.

The LLM will eventually populate these models. This module deliberately does
not know about prompts, providers, HTTP, or database implementation. It only
normalizes what the customer appears to want into semantic intents that the
planner can turn into executable actions.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .contracts import ToolName
from .state import LanguageMode


class IntentType(StrEnum):
    """Customer-level intent names understood by the V1 planner."""

    STORE_CONTEXT = "store_context"
    PRODUCT_SEARCH = "product_search"
    PRODUCT_DETAILS = "product_details"
    BRANCH_INFORMATION = "branch_information"
    AVAILABILITY_CHECK = "availability_check"
    CREATE_CART = "create_cart"
    VIEW_CART = "view_cart"
    ADD_TO_CART = "add_to_cart"
    UPDATE_CART = "update_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    CLEAR_CART = "clear_cart"
    CHECKOUT = "checkout"
    PLACE_ORDER = "place_order"
    GENERAL_CONVERSATION = "general_conversation"


class IntentRequest(BaseModel):
    """One normalized customer intent produced by the intent extractor.

    ``parameters`` contains only information actually extracted or explicitly
    referenced by the customer. Missing values are intentionally left out so
    the requirement checker can determine what must be requested next.
    """

    model_config = ConfigDict(extra="forbid")

    intent_id: str = Field(min_length=1)
    intent_type: IntentType
    parameters: dict[str, Any] = Field(default_factory=dict)
    explicit_confirmation: bool | None = None
    customer_choice_required: bool = False


class IntentExtraction(BaseModel):
    """Complete normalized result for one customer message.

    Multiple intents are allowed. The planner enforces actual dependencies,
    required parameters, and customer-confirmation boundaries.
    """

    model_config = ConfigDict(extra="forbid")

    language: LanguageMode
    intents: list[IntentRequest] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Return True when no actionable intent was extracted."""

        return not self.intents


def intent_to_tool(intent_type: IntentType) -> ToolName | None:
    """Map a semantic customer intent to the canonical tool contract."""

    mapping: dict[IntentType, ToolName] = {
        IntentType.STORE_CONTEXT: ToolName.GET_STORE_CONTEXT,
        IntentType.PRODUCT_SEARCH: ToolName.GET_PRODUCTS,
        IntentType.PRODUCT_DETAILS: ToolName.GET_PRODUCT_DETAILS,
        IntentType.BRANCH_INFORMATION: ToolName.GET_BRANCHES,
        IntentType.AVAILABILITY_CHECK: ToolName.CHECK_AVAILABILITY,
        IntentType.CREATE_CART: ToolName.CREATE_CART,
        IntentType.VIEW_CART: ToolName.GET_CART,
        IntentType.ADD_TO_CART: ToolName.ADD_TO_CART,
        IntentType.UPDATE_CART: ToolName.UPDATE_CART,
        IntentType.REMOVE_FROM_CART: ToolName.REMOVE_FROM_CART,
        IntentType.CLEAR_CART: ToolName.CLEAR_CART,
        IntentType.CHECKOUT: ToolName.PREVIEW_CHECKOUT,
        IntentType.PLACE_ORDER: ToolName.PLACE_ORDER,
    }
    return mapping.get(intent_type)
