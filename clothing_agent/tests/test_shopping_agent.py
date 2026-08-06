from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.agents.schemas import AgentRequest
from app.agents.shopping.service import ShoppingAgent
from app.clients.clothing_app.schemas import BranchView, ProductOption, ProductSearchResponse
from app.core.config import AgentConfig
from app.core.conversation import ConversationState, ShoppingPreferences
from app.llm.client import LLMClient
from app.core.routing import AgentName, Intent, RouteDecision


class FakeHttp:
    async def post(self, *args, **kwargs):
        raise AssertionError("LLM should not be called")


class FakeClothingAppClient:
    def __init__(self):
        self.search_calls = 0

    async def search_products(self, request):
        self.search_calls += 1
        return ProductSearchResponse(
            products=[
                ProductOption(
                    product_id=1,
                    variant_id=11,
                    branch_id=21,
                    article_code="SH-001",
                    product_name="Relaxed Summer Shirt",
                    category="Shirts",
                    gender="Men",
                    brand="Demo",
                    color="White",
                    size="M",
                    price=Decimal("3490"),
                    branch_code="LHR-01",
                    branch_name="Lahore Main",
                    city="Lahore",
                    available_quantity=3,
                    fit="relaxed",
                    material="cotton",
                )
            ],
            result_count=1,
        )

    async def get_product(self, product_id):
        raise AssertionError("not used")

    async def get_availability(self, variant_id, branch_id):
        raise AssertionError("not used")

    async def list_branches(self):
        return [
            BranchView(
                branch_id=21,
                branch_code="LHR-01",
                branch_name="Lahore Main",
                city="Lahore",
                address="Demo address",
            )
        ]


def build_agent():
    config = AgentConfig(llm_api_key=None, displayed_product_limit=3)
    client = FakeClothingAppClient()
    agent = ShoppingAgent(LLMClient(config, FakeHttp()), client, config)
    return agent, client


def state(**updates):
    now = datetime.now(timezone.utc)
    payload = dict(conversation_id=uuid4(), created_at=now, updated_at=now)
    payload.update(updates)
    return ConversationState(**payload)


@pytest.mark.asyncio
async def test_broad_category_asks_before_searching():
    agent, client = build_agent()
    result = await agent.handle(
        AgentRequest(
            message="I want to buy shirts",
            context=state(),
            route=RouteDecision(intent=Intent.PRODUCT_SEARCH, target_agent=AgentName.SHOPPING),
        )
    )
    assert client.search_calls == 0
    assert "casual" in result.reply.lower()
    assert "office/formal" in result.reply.lower()
    assert result.state_updates["clarification_count"] == 1


@pytest.mark.asyncio
async def test_second_answer_completes_guided_search():
    agent, client = build_agent()
    context = state(
        shopping_stage="clarifying",
        clarification_count=2,
        preferences=ShoppingPreferences(
            category="shirts",
            purpose="casual",
            semantic_tags=["casual", "summer"],
        ),
    )
    result = await agent.handle(
        AgentRequest(
            message="relaxed fit",
            context=context,
            route=RouteDecision(intent=Intent.PRODUCT_SEARCH, target_agent=AgentName.SHOPPING),
        )
    )
    assert client.search_calls == 1
    assert result.products[0].product_name == "Relaxed Summer Shirt"
    assert result.state_updates["preferences"].fits == ["relaxed"]


@pytest.mark.asyncio
async def test_specific_request_searches_immediately():
    agent, client = build_agent()
    result = await agent.handle(
        AgentRequest(
            message="Show me black shirts size M under 5000",
            context=state(),
            route=RouteDecision(intent=Intent.PRODUCT_SEARCH, target_agent=AgentName.SHOPPING),
        )
    )
    assert client.search_calls == 1
    assert result.products


@pytest.mark.asyncio
async def test_first_guided_answer_shows_products_without_fit_interview():
    agent, client = build_agent()
    context = state(
        shopping_stage="clarifying",
        clarification_count=1,
        preferences=ShoppingPreferences(category="shirts"),
    )
    result = await agent.handle(
        AgentRequest(
            message="casual for summer",
            context=context,
            route=RouteDecision(intent=Intent.PRODUCT_SEARCH, target_agent=AgentName.SHOPPING),
        )
    )
    assert client.search_calls == 1
    assert result.products
    assert "fit" not in result.reply.lower()
