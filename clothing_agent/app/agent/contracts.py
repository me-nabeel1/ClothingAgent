"""Contracts used to describe Agent tools and their execution requirements.

This module intentionally contains no LLM, HTTP, or business-rule code.  It
exists so every tool exposes a machine-readable contract that the generic
requirement checker and later execution planner can consume consistently.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolName(StrEnum):
    """Stable semantic names for Agent capabilities.

    These names describe what Fitzy wants to accomplish.  The integration
    adapter decides which concrete application endpoint implements the
    capability.
    """

    GET_STORE_CONTEXT = "get_store_context"
    GET_PRODUCTS = "get_products"
    GET_PRODUCT_DETAILS = "get_product_details"
    GET_BRANCHES = "get_branches"
    CHECK_AVAILABILITY = "check_availability"
    CREATE_CART = "create_cart"
    GET_CART = "get_cart"
    ADD_TO_CART = "add_to_cart"
    UPDATE_CART = "update_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    CLEAR_CART = "clear_cart"
    PREVIEW_CHECKOUT = "preview_checkout"
    PLACE_ORDER = "place_order"


class ParameterDefinition(BaseModel):
    """Describe one input accepted by a semantic tool contract.

    ``required`` only means that the tool cannot execute without a usable
    value.  It does not mean the customer must explicitly provide it; the
    value may already exist in conversation state or be deterministically
    resolved by another completed action.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required: bool = False
    allow_state_value: bool = True
    allow_derived_value: bool = True


class ToolContract(BaseModel):
    """Machine-readable contract for one Agent capability.

    The contract is deliberately independent from HTTP endpoint details.  A
    later integration adapter can map the semantic capability to any real
    application's API without changing Fitzy's planning/requirement logic.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: ToolName
    description: str = Field(min_length=1)
    parameters: tuple[ParameterDefinition, ...] = Field(default_factory=tuple)
    mutates_customer_state: bool = False
    requires_explicit_confirmation: bool = False

    @property
    def required_parameters(self) -> tuple[ParameterDefinition, ...]:
        """Return the parameters that must be resolved before execution."""

        return tuple(parameter for parameter in self.parameters if parameter.required)


class ToolInvocation(BaseModel):
    """Represent a planned tool invocation with currently known parameters."""

    model_config = ConfigDict(extra="forbid")

    tool_name: ToolName
    parameters: dict[str, Any] = Field(default_factory=dict)
    dependency_ids: tuple[str, ...] = Field(default_factory=tuple)
    request_id: str | None = None


class RequirementCheckResult(BaseModel):
    """Result returned by the generic tool requirement checker."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool_name: ToolName
    ready: bool
    resolved_parameters: dict[str, Any] = Field(default_factory=dict)
    missing_parameters: tuple[str, ...] = Field(default_factory=tuple)
    invalid_parameters: tuple[str, ...] = Field(default_factory=tuple)
    reason: str | None = None


# ---------------------------------------------------------------------------
# V1 tool contracts.
# These are intentionally semantic.  Exact API paths are kept separately in
# ``app.integration.api_map`` so the Agent does not become coupled to them.
# ---------------------------------------------------------------------------

GET_STORE_CONTEXT = ToolContract(
    name=ToolName.GET_STORE_CONTEXT,
    description="Load the connected store's capabilities, catalog vocabulary, and branches.",
)

GET_PRODUCTS = ToolContract(
    name=ToolName.GET_PRODUCTS,
    description="Retrieve products matching any subset of structured shopping filters.",
    parameters=(
        ParameterDefinition(name="query_text", description="Free-text catalog query."),
        ParameterDefinition(name="categories", description="Requested product categories."),
        ParameterDefinition(name="product_types", description="Requested product types."),
        ParameterDefinition(name="occasions", description="Requested occasions or purposes."),
        ParameterDefinition(name="colors", description="Preferred colors."),
        ParameterDefinition(name="excluded_colors", description="Colors the customer does not want."),
        ParameterDefinition(name="size_mapping", description="Semantic size mapping such as shirt=L or pants=34."),
        ParameterDefinition(name="minimum_price", description="Minimum acceptable price."),
        ParameterDefinition(name="maximum_price", description="Maximum acceptable price."),
        ParameterDefinition(name="branch_code", description="Explicit branch constraint when the customer asks about a branch."),
        ParameterDefinition(name="article_code", description="Exact article identifier."),
        ParameterDefinition(name="sku", description="Exact SKU."),
        ParameterDefinition(name="in_stock_only", description="Whether discovery should prioritize/require purchasable variants."),
        ParameterDefinition(name="limit", description="Maximum number of products to retrieve."),
    ),
)

GET_PRODUCT_DETAILS = ToolContract(
    name=ToolName.GET_PRODUCT_DETAILS,
    description="Retrieve authoritative details for one known product.",
    parameters=(
        ParameterDefinition(name="product_id", description="Stable product identifier."),
    ),
)

GET_BRANCHES = ToolContract(
    name=ToolName.GET_BRANCHES,
    description="Return the store's available branches for customer branch questions.",
)

CHECK_AVAILABILITY = ToolContract(
    name=ToolName.CHECK_AVAILABILITY,
    description="Check one exact variant in one explicit branch.",
    parameters=(
        ParameterDefinition(name="variant_id", description="Exact sellable variant identifier.", required=True),
        ParameterDefinition(name="branch_id", description="Internal branch identifier used by the existing API.", required=True),
    ),
)

CREATE_CART = ToolContract(
    name=ToolName.CREATE_CART,
    description="Create a persistent cart for the current session.",
    mutates_customer_state=True,
)

GET_CART = ToolContract(
    name=ToolName.GET_CART,
    description="Read the current cart for the customer session.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
    ),
)

ADD_TO_CART = ToolContract(
    name=ToolName.ADD_TO_CART,
    description="Add a specific sellable product variant to the current cart.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
        ParameterDefinition(name="variant_id", description="Exact sellable variant identifier.", required=True),
        ParameterDefinition(name="branch_id", description="Internal fulfillment/availability branch identifier.", required=True),
        ParameterDefinition(name="quantity", description="Number of units to add.", required=True),
    ),
    mutates_customer_state=True,
)

UPDATE_CART = ToolContract(
    name=ToolName.UPDATE_CART,
    description="Replace the quantity of one existing cart item.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
        ParameterDefinition(name="item_id", description="Cart item identifier.", required=True),
        ParameterDefinition(name="quantity", description="New quantity.", required=True),
    ),
    mutates_customer_state=True,
)

REMOVE_FROM_CART = ToolContract(
    name=ToolName.REMOVE_FROM_CART,
    description="Remove one item from the current cart.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
        ParameterDefinition(name="item_id", description="Cart item identifier.", required=True),
    ),
    mutates_customer_state=True,
)

CLEAR_CART = ToolContract(
    name=ToolName.CLEAR_CART,
    description="Clear all items from the current cart.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
    ),
    mutates_customer_state=True,
)

PREVIEW_CHECKOUT = ToolContract(
    name=ToolName.PREVIEW_CHECKOUT,
    description="Calculate the authoritative checkout totals for the current cart.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
    ),
)

PLACE_ORDER = ToolContract(
    name=ToolName.PLACE_ORDER,
    description="Create the final order from the current cart using the existing commerce API.",
    parameters=(
        ParameterDefinition(name="cart_id", description="Current cart identifier.", required=True),
        ParameterDefinition(name="customer_name", description="Customer delivery name.", required=True),
        ParameterDefinition(name="phone", description="Customer phone number.", required=True),
        ParameterDefinition(name="delivery_address", description="Full delivery address.", required=True),
        ParameterDefinition(name="city", description="Delivery city.", required=True),
        ParameterDefinition(name="delivery_notes", description="Optional delivery notes."),
        ParameterDefinition(name="explicit_confirmation", description="Whether the customer explicitly confirmed the final order.", required=True),
    ),
    mutates_customer_state=True,
    requires_explicit_confirmation=True,
)

ALL_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    GET_STORE_CONTEXT,
    GET_PRODUCTS,
    GET_PRODUCT_DETAILS,
    GET_BRANCHES,
    CHECK_AVAILABILITY,
    CREATE_CART,
    GET_CART,
    ADD_TO_CART,
    UPDATE_CART,
    REMOVE_FROM_CART,
    CLEAR_CART,
    PREVIEW_CHECKOUT,
    PLACE_ORDER,
)

TOOL_CONTRACTS: dict[ToolName, ToolContract] = {
    contract.name: contract for contract in ALL_TOOL_CONTRACTS
}
