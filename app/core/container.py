"""Dependency composition for the complete agent application."""

from __future__ import annotations

from functools import lru_cache

import httpx
from app.clients.clothing_app.client import ClothingAppClient
from app.core.config import AgentConfig, get_config
from app.llm.client import LLMClient
from app.context.store import StoreContextManager


class AppContainer:
    """Build repositories and clients."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient()
        self.clothing_app = ClothingAppClient(config, self.http)
        self.llm = LLMClient(config, self.http)
        self.store_context = StoreContextManager(self.clothing_app)

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())

