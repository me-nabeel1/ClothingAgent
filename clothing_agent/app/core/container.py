"""Dependency composition for the complete agent application."""

from __future__ import annotations

from functools import lru_cache

import httpx
from app.clients.clothing_app.client import ClothingAppClient
from app.core.config import AgentConfig, get_config
from app.llm.client import LLMClient
from app.context.store import StoreContextManager
from app.agent.tools import AgentTools
from app.agent.intent import IntentExtractor
from app.agent.agent import SingleAgent
from app.core.state_store import FileConversationStateStore


class AppContainer:
    """Build repositories, clients, tools, and the single agent once."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient()
        self.clothing_app = ClothingAppClient(config, self.http)
        self.llm = LLMClient(config, self.http)
        
        # New Single Agent Foundation
        self.store_context = StoreContextManager(self.clothing_app)
        self.tools = AgentTools(self.clothing_app)
        self.intent_extractor = IntentExtractor(self.llm)
        self.agent = SingleAgent(self.llm, self.intent_extractor, self.tools)
        self.state_store = FileConversationStateStore(config.state_dir)

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())
