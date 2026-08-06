from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.config import AgentConfig
from app.core.conversation import ConversationState
from app.llm.client import LLMClient
from app.core.routing import AgentName, Intent, RouterService, route_by_rules


class FakeHttp:
    async def post(self, *args, **kwargs):
        raise AssertionError("LLM should not be called")


def test_greeting_routes_to_sales_agent():
    route = route_by_rules("Hello")
    assert route is not None
    assert route.intent == Intent.GREETING
    assert route.target_agent == AgentName.SALES


def test_product_search_routes_to_shopping_agent():
    route = route_by_rules("Show me black shirts under 5000")
    assert route is not None
    assert route.intent == Intent.PRODUCT_SEARCH
    assert route.target_agent == AgentName.SHOPPING


def test_ordinal_only_routes_to_product_selection():
    route = route_by_rules("the second one")
    assert route is not None
    assert route.intent == Intent.PRODUCT_SELECTION


def test_unrelated_politics_is_rejected():
    route = route_by_rules("Tell me about politics and elections")
    assert route is not None
    assert route.intent == Intent.OUT_OF_DOMAIN


@pytest.mark.asyncio
async def test_short_answer_continues_clarification_flow():
    config = AgentConfig(llm_api_key=None)
    router = RouterService(LLMClient(config, FakeHttp()), config)
    now = datetime.now(timezone.utc)
    context = ConversationState(
        conversation_id=uuid4(),
        shopping_stage="clarifying",
        clarification_count=1,
        created_at=now,
        updated_at=now,
    )
    route = await router.route("relaxed", context)
    assert route.intent == Intent.PRODUCT_SEARCH
    assert route.target_agent == AgentName.SHOPPING
