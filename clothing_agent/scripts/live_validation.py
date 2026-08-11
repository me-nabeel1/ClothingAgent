"""Live Integration Pipeline Validation for Agent V1."""

import asyncio
import httpx
from typing import List, Dict, Any

from app.core.config import get_config
from app.llm.client import LLMClient
from app.clients.clothing_app.client import ClothingAppClient
from app.agent.tools import AgentTools
from app.agent.intent import IntentExtractor
from app.agent.agent import SingleAgent
from app.agent.state import ConversationState

async def print_conversation(role: str, message: str):
    print(f"\n[{role.upper()}]")
    print(f"{message}")
    print("-" * 40)

async def run_scenario(name: str, agent: SingleAgent, state: ConversationState, store_context: Any, messages: List[str]):
    print(f"\n{'='*50}")
    print(f"RUNNING SCENARIO: {name}")
    print(f"{'='*50}")
    
    for msg in messages:
        await print_conversation("user", msg)
        response = await agent.process_message(msg, state, store_context)
        await print_conversation("agent", response)

async def main():
    config = get_config()
    
    async with httpx.AsyncClient() as http_client:
        llm = LLMClient(config, http_client)
        backend = ClothingAppClient(config, http_client)
        tools = AgentTools(backend)
        extractor = IntentExtractor(llm)
        agent = SingleAgent(llm, extractor, tools)
        
        # Load store context
        print("Loading Store Context...")
        store_context = await backend.get_store_context()
        print(f"Connected to: {store_context.store_name}")
        
        # We will use one continuous state for most scenarios to test preference retention
        state = ConversationState(session_id="live_test_session_1")
        
        # Scenario A — English broad search
        await run_scenario("Scenario A — English broad search", agent, state, store_context, [
            "I need something for a wedding."
        ])
        
        # Scenario B — Roman Urdu broad search
        await run_scenario("Scenario B — Roman Urdu broad search", agent, state, store_context, [
            "mujhe shadi ke liye kuch acha sa chahiye"
        ])
        
        # Scenario C — Specific search
        await run_scenario("Scenario C — Specific search", agent, state, store_context, [
            "Show me black shirts under 5000 in large."
        ])
        
        # Scenario D — Preference update
        await run_scenario("Scenario D — Preference update", agent, state, store_context, [
            "I usually like black.",
            "Actually, show me white shirts."
        ])
        
        # Scenario E — Multiple categories
        await run_scenario("Scenario E — Multiple categories", agent, state, store_context, [
            "Show me jackets and hoodies."
        ])
        
        # Scenario F — Branch availability
        await run_scenario("Scenario F — Branch availability", agent, state, store_context, [
            "Are these available in Islamabad?"
        ])
        
        # Scenario G — Exact unavailable item
        await run_scenario("Scenario G — Exact unavailable item", agent, state, store_context, [
            "Do you have article NS-SH-999?"
        ])
        
        # Scenario H — Product details
        await run_scenario("Scenario H — Product details", agent, state, store_context, [
            "Show me basic shirts.",
            "Tell me more about product 1."
        ])
        
        # Scenario I — Cart
        await run_scenario("Scenario I — Cart", agent, state, store_context, [
            "Add it to my cart."
        ])
        
        # Scenario J — Checkout
        await run_scenario("Scenario J — Checkout", agent, state, store_context, [
            "Checkout.",
            "I am Nabeel, phone is 03001234567 and I live at House 10, F-7 Islamabad."
        ])
        
        # Scenario K — Confirmation
        await run_scenario("Scenario K — Confirmation", agent, state, store_context, [
            "Yes, place it."
        ])
        
        # Scenario L — Urdu checkout (New Session)
        state_urdu = ConversationState(session_id="live_test_session_urdu_2")
        await run_scenario("Scenario L — Urdu checkout", agent, state_urdu, store_context, [
            "mujhe ek black shirt chahiye",
            "product 1 add kar lo cart mein. size medium",
            "ab checkout karna hai",
            "mera naam Ali hai, number 03009999999, address DHA Lahore",
            "haan, order place kar do"
        ])
        
        print("\nAll Scenarios executed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
