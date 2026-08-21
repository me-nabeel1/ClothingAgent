"""Phase 1 tests for contracts, requirements, and conversation state."""

from decimal import Decimal

import pytest

from clothing_agent.app.agent.contracts import (
    ADD_TO_CART,
    PLACE_ORDER,
    ToolName,
)
from clothing_agent.app.agent.requirements import ToolRequirementChecker
from clothing_agent.app.agent.state import ActionStatus, ConversationState


def test_add_to_cart_requires_only_execution_critical_parameters() -> None:
    """The generic checker blocks execution when mandatory values are absent."""

    result = ToolRequirementChecker().check(
        ADD_TO_CART,
        provided_parameters={"cart_id": "cart-1", "variant_id": 10},
    )

    assert result.ready is False
    assert result.missing_parameters == ("branch_id", "quantity")


def test_add_to_cart_can_resolve_required_values_from_state() -> None:
    """Previously established state values may satisfy a tool requirement."""

    result = ToolRequirementChecker().check(
        ADD_TO_CART,
        provided_parameters={"cart_id": "cart-1"},
        state_values={"variant_id": 10, "branch_id": 3, "quantity": 1},
    )

    assert result.ready is True
    assert result.resolved_parameters["variant_id"] == 10


def test_place_order_requires_explicit_confirmation() -> None:
    """Order placement is blocked until the explicit customer confirmation is true."""

    checker = ToolRequirementChecker()
    base = {
        "cart_id": "cart-1",
        "customer_name": "Ahmed",
        "phone": "03001234567",
        "delivery_address": "House 1, F-7",
        "city": "Islamabad",
    }

    not_confirmed = checker.check(
        PLACE_ORDER,
        provided_parameters={**base, "explicit_confirmation": False},
    )
    confirmed = checker.check(
        PLACE_ORDER,
        provided_parameters={**base, "explicit_confirmation": True},
    )

    assert not_confirmed.ready is False
    assert "explicit_confirmation" in not_confirmed.invalid_parameters
    assert confirmed.ready is True


def test_search_state_updates_without_clearing_other_filters() -> None:
    """Incremental search updates preserve existing unrelated filters."""

    state = ConversationState()
    state.current_search.update_from_mapping({
        "occasions": ["wedding"],
        "colors": ["black"],
        "maximum_price": Decimal("5000"),
    })
    state.current_search.update_from_mapping({"colors": ["blue"]})

    assert state.current_search.occasions == ["wedding"]
    assert state.current_search.colors == ["blue"]
    assert state.current_search.maximum_price == Decimal("5000")


def test_reset_current_search_preserves_preferences_and_cart() -> None:
    """Clearing temporary search state must not clear long-lived customer state."""

    state = ConversationState()
    state.preferences.preferred_colors = ["black"]
    state.cart.item_count = 2
    state.current_search.update_from_mapping({"categories": ["shirts"]})

    state.reset_current_search()

    assert state.current_search.categories == []
    assert state.preferences.preferred_colors == ["black"]
    assert state.cart.item_count == 2


def test_action_plan_ready_actions_respect_dependencies() -> None:
    """An action is ready only when every declared dependency is complete."""

    state = ConversationState()
    search = state.action_plan.actions
    first = state.action_plan.actions
    del search[:]

    from clothing_agent.app.agent.state import PlannedAction

    a = PlannedAction(tool_name=ToolName.GET_PRODUCTS, status=ActionStatus.COMPLETED)
    b = PlannedAction(tool_name=ToolName.GET_PRODUCT_DETAILS, dependency_ids=[a.action_id])
    state.action_plan.actions.extend([a, b])

    ready = state.action_plan.ready_actions()

    assert ready == [b]


@pytest.mark.parametrize("value", [None, "", "   ", [], {}, ()])
def test_empty_required_values_are_not_treated_as_satisfied(value) -> None:
    """Blank containers/strings must not satisfy mandatory tool parameters."""

    result = ToolRequirementChecker().check(
        ADD_TO_CART,
        provided_parameters={
            "cart_id": "cart-1",
            "variant_id": 10,
            "branch_id": value,
            "quantity": 1,
        },
    )

    assert result.ready is False
    assert "branch_id" in result.missing_parameters
