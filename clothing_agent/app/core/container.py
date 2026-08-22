"""Dependency composition for the complete agent application."""

from __future__ import annotations

from functools import lru_cache

import httpx
from app.core.config import AgentConfig, get_config
from app.llm.client import OpenAICompatibleLLMClient
from app.agent.agent import FitzyAgent
from app.integration.client import CommerceAPIClient, CommerceToolAdapter
from app.integration.http import AsyncJSONTransport


class AppContainer:
    """Build repositories, clients, tools, and the Fitzy agent once."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient(base_url=config.clothing_app_base_url, timeout=config.clothing_app_timeout_seconds)
        self.transport = AsyncJSONTransport(config.clothing_app_base_url, client=self.http)
        self.commerce_client = CommerceAPIClient(self.transport, {})
        self.tool_adapter = CommerceToolAdapter(self.commerce_client)
        self.llm = OpenAICompatibleLLMClient(
            base_url=config.llm_api_base,
            api_key=config.llm_api_key,
            model=config.llm_model,
            timeout_seconds=config.llm_timeout_seconds,
        )
        self.fitzy_agent = FitzyAgent(llm=self.llm, tools=self.tool_adapter)

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())
