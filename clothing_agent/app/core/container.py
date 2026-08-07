"""Dependency composition for the complete agent application."""

from __future__ import annotations

from functools import lru_cache

import httpx

from app.clients.clothing_app.client import ClothingAppClient

from app.core.config import AgentConfig, get_config
from app.core.chat import OrchestratorService
from app.core.conversation import ConversationRepository, ConversationService
from app.llm.client import LLMClient
from app.llm.agent import MonolithicAgentService


class AppContainer:
    """Build repositories, clients, tools, agents, and orchestration once."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient()
        self.clothing_app = ClothingAppClient(config, self.http)
        self.llm = LLMClient(config, self.http)

        self.conversations = ConversationService(ConversationRepository())

        self.agent = MonolithicAgentService(self.llm, self.clothing_app, config)
        
        self.orchestrator = OrchestratorService(
            self.conversations,
            self.agent,
            config,
        )

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())
