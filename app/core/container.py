"""Dependency composition for the complete agent application."""

from __future__ import annotations

import os
from functools import lru_cache

import httpx
from app.clients.clothing_app.client import ClothingAppClient
from app.core.config import AgentConfig, get_config
from app.context.store import StoreContextManager

from clothing_agent.app.agent.agent import FitzyAgent
from clothing_agent.app.agent.tools import AgentTools
from clothing_agent.app.integration.client import CommerceAPIClient, CommerceToolAdapter
from clothing_agent.app.integration.http import AsyncJSONTransport
from clothing_agent.app.llm.client import OpenAICompatibleLLMClient, FakeLLMClient
from clothing_agent.app.agent.intent import IntentExtraction, IntentRequest, IntentType
from clothing_agent.app.agent.state import LanguageMode


class AppContainer:
    """Build repositories, clients, and the singleton FitzyAgent instance."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.http = httpx.AsyncClient()
        self.clothing_app = ClothingAppClient(config, self.http)
        self.store_context = StoreContextManager(self.clothing_app)

        # Initialize LLM client (OpenAI-compatible or fallback double if unconfigured)
        api_key = os.getenv("FITZY_LLM_API_KEY")
        model = os.getenv("FITZY_LLM_MODEL")
        if api_key and model:
            self.llm = OpenAICompatibleLLMClient(
                base_url=os.getenv("FITZY_LLM_BASE_URL", "https://api.openai.com/v1"),
                api_key=api_key,
                model=model,
            )
        else:
            # Fallback FakeLLMClient for unconfigured environments
            default_extraction = IntentExtraction(
                language=LanguageMode.ENGLISH,
                intents=[IntentRequest(intent_id="1", intent_type=IntentType.GENERAL_CONVERSATION)],
            )
            self.llm = FakeLLMClient(default_extraction, "Welcome to Northstar! How can I assist you with your shopping today?")

        # Integration & Adapter Layer
        base_url = config.clothing_app_base_url.rstrip("/")
        self.agent_transport = AsyncJSONTransport(base_url, client=self.http)
        self.commerce_client = CommerceAPIClient(self.agent_transport, {})
        self.tool_adapter = CommerceToolAdapter(self.commerce_client)
        self.agent_tools = AgentTools(self.tool_adapter)

        # Fitzy Runtime Agent Singleton
        self.fitzy_agent = FitzyAgent(llm=self.llm, tools=self.agent_tools)

    async def close(self) -> None:
        """Release shared HTTP connections during shutdown."""

        await self.http.aclose()


@lru_cache
def get_container() -> AppContainer:
    """Return the process-wide dependency container."""

    return AppContainer(get_config())


