"""Dependency composition for the complete agent application."""

from __future__ import annotations

from functools import lru_cache

import httpx
from app.agents.cart.service import CartAgent
from app.agents.fashion.service import FashionAgent
from app.agents.registry import AgentRegistry
from app.agents.sales.service import SalesAgent
from app.agents.shopping.service import ShoppingAgent
from app.clients.clothing_app.client import ClothingAppClient
from app.core.chat import OrchestratorService
from app.core.config import AgentConfig, get_config
from app.core.conversation import ConversationRepository, ConversationService
from app.core.routing import AgentName, RouterService
from app.llm.client import LLMClient


class AppContainer:
    """Build repositories, clients, tools, agents, and orchestration once."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient()
        self.clothing_app = ClothingAppClient(config, self.http)
        self.llm = LLMClient(config, self.http)

        self.conversations = ConversationService(ConversationRepository())

        self.agents = AgentRegistry()
        self.agents.register(AgentName.SALES, SalesAgent(self.llm, config))
        self.agents.register(
            AgentName.SHOPPING,
            ShoppingAgent(self.llm, self.clothing_app, config),
        )
        self.agents.register(
            AgentName.FASHION,
            FashionAgent(self.llm, self.clothing_app, config),
        )
        self.agents.register(
            AgentName.CART,
            CartAgent(self.llm, self.clothing_app, config),
        )

        self.router = RouterService(self.llm, config)
        self.orchestrator = OrchestratorService(
            self.conversations,
            self.router,
            self.agents,
            config,
        )

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())
