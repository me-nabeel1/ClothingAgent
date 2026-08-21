from decimal import Decimal

import pytest

from clothing_agent.app.agent.agent import FitzyAgent
from clothing_agent.app.agent.contracts import ToolName
from clothing_agent.app.agent.intent import IntentExtraction, IntentRequest, IntentType
from clothing_agent.app.agent.state import ConversationState, LanguageMode


class StubLLM:
    async def generate_structured(self, *, system_prompt, user_message, response_model):
        return IntentExtraction(
            language=LanguageMode.ENGLISH,
            intents=[IntentRequest(intent_id="search", intent_type=IntentType.PRODUCT_SEARCH, parameters={"colors": ["blue"]})],
        )

    async def generate_text(self, *, system_prompt, user_message):
        return "Here are the available options."


@pytest.mark.asyncio
async def test_effective_search_preserves_existing_context():
    agent = object.__new__(FitzyAgent)
    state = ConversationState()
    state.current_search.colors = ["black"]
    state.current_search.maximum_price = Decimal("5000")
    values = agent._build_effective_product_search(state, {"colors": ["blue"]})
    assert values["colors"] == ["blue"]
    assert values["maximum_price"] == Decimal("5000")
    assert values.get("size_mapping", {}) == {}

@pytest.mark.asyncio
async def test_delivery_information_accumulates_across_turns():
    agent = object.__new__(FitzyAgent)
    state = ConversationState()
    agent._apply_delivery_fields({"customer_name": "Ahmed"}, state)
    agent._apply_delivery_fields({"phone": "0300"}, state)
    agent._apply_delivery_fields({"delivery_address": "DHA Lahore", "city": "Lahore"}, state)
    assert state.delivery.customer_name == "Ahmed"
    assert state.delivery.phone == "0300"
    assert state.delivery.delivery_address == "DHA Lahore"
    assert state.delivery.city == "Lahore"
    assert state.has_complete_delivery_details()

@pytest.mark.asyncio
async def test_waiting_action_reopens_on_new_turn():
    agent = object.__new__(FitzyAgent)
    state = ConversationState()
    from clothing_agent.app.agent.state import PlannedAction, ActionStatus
    pending = PlannedAction(tool_name=ToolName.PLACE_ORDER, status=ActionStatus.WAITING_FOR_INPUT, missing_parameters=["city"])
    state.action_plan.actions.append(pending)
    state.pending_action_id = pending.action_id
    agent._reopen_waiting_actions_for_new_input(state)
    assert pending.status == ActionStatus.PENDING
    assert pending.missing_parameters == []
