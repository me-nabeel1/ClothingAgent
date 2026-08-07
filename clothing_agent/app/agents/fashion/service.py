"""Fashion advice with optional inventory grounding."""

from __future__ import annotations

from app.agents.schemas import AgentRequest, AgentResult
from app.clients.clothing_app.schemas import ProductSearchRequest, ProductSearchResponse
from app.core.config import AgentConfig
from app.core.errors import DependencyUnavailableError
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import FASHION_PROMPT
from app.clients.clothing_app.client import ClothingAppClient
from pydantic import BaseModel, Field


class FashionPlan(BaseModel):
    """Advice plus an optional inventory search derived from that advice."""

    advice: str
    should_search_inventory: bool = False
    search_request: ProductSearchRequest | None = None
    suggested_actions: list[str] = Field(default_factory=list)


class FashionAgent:
    """Guide customers on styling and optionally retrieve matching products."""

    def __init__(
        self,
        llm: LLMClient,
        client: ClothingAppClient,
        config: AgentConfig,
    ) -> None:
        self._llm = llm
        self._client = client
        self._config = config

    async def handle(self, request: AgentRequest) -> AgentResult:
        """Return domain-limited fashion advice and grounded product options."""

        plan = await self._plan(request)
        products = []
        reply = plan.advice
        if plan.should_search_inventory and plan.search_request:
            result = await self._client.search_products(plan.search_request)
            assert isinstance(result, ProductSearchResponse)
            products = result.products
            if products:
                reply += f" I also found {len(products)} matching in-stock option(s) in the store."
        return AgentResult(
            reply=reply,
            products=products,
            suggested_actions=plan.suggested_actions,
        )

    async def _plan(self, request: AgentRequest) -> FashionPlan:
        """Create a fashion plan through the LLM with a practical fallback."""

        if self._llm.configured:
            try:
                messages = [LLMMessage(role="system", content=FASHION_PROMPT)]
                for msg in request.context.messages[-self._config.recent_message_limit :]:
                    messages.append(LLMMessage(role=msg.role, content=msg.content))
                return await self._llm.generate_structured(
                    messages,
                    FashionPlan,
                )
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise
        text = request.message.lower()
        if "summer" in text or "hot" in text:
            advice = "For hot weather, choose breathable cotton or linen, lighter colors, and a relaxed or regular fit."
            search = ProductSearchRequest(
                query_text=request.message,
                materials=["cotton", "linen"],
                semantic_tags=["summer", "breathable", "comfortable"],
                limit=self._config.displayed_product_limit,
            )
        elif "formal" in text or "office" in text:
            advice = "For a polished office look, pair a white or light-blue shirt with navy, charcoal, or beige trousers and keep the fit tailored but comfortable."
            search = ProductSearchRequest(
                query_text=request.message,
                semantic_tags=["formal", "office"],
                limit=self._config.displayed_product_limit,
            )
        else:
            advice = "Build the outfit around the occasion, then balance color, fit, and comfort. Neutral trousers work well with one stronger color or texture on top."
            search = None
        wants_products = any(term in text for term in ("show", "find", "options", "products"))
        return FashionPlan(
            advice=advice,
            should_search_inventory=wants_products and search is not None,
            search_request=search if wants_products else None,
            suggested_actions=["Show matching products", "Refine by budget"],
        )
