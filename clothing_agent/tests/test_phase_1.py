import pytest
from uuid import UUID

from app.clients.port import BackendPort
from app.clients.clothing_app.client import ClothingAppClient
from app.agent.registry import TOOL_REGISTRY, register_all_tools
from app.agent.checker import ParameterRequirementsChecker
from app.agent.state import ConversationState

from app.agent.schemas import (
    ExploreCategoryPayload,
    SearchProductsPayload,
    GetProductDetailsPayload,
    AddCartItemPayload,
    RemoveCartItemPayload,
    ShowCartPayload,
    PreviewCheckoutPayload,
    PlaceOrderPayload,
    GetPromotionsPayload,
    UpdateCartItemPayload,
    ClearCartPayload,
    CheckAvailabilityPayload,
    GetOrderStatusPayload
)

def test_backend_port_compliance():
    """Verify ClothingAppClient inherits from BackendPort, despite missing get_order."""
    assert issubclass(ClothingAppClient, BackendPort)
    
    from app.core.config import AgentConfig
    from httpx import AsyncClient
    
    config = AgentConfig()
    client = ClothingAppClient(config, AsyncClient())
    assert isinstance(client, BackendPort)

@pytest.mark.asyncio
async def test_tool_registry():
    # Clear registry for testing
    TOOL_REGISTRY.clear()
    
    # Dummy tools instance
    class DummyTools:
        async def search(self, state, payload): pass
        async def search(self, state, payload): pass
        async def get_details(self, payload, state): pass
        async def add_to_cart(self, state, payload): pass
        async def remove_cart(self, state, payload): pass
        async def checkout(self, state): pass
        async def place_order(self, state, payload): pass
        async def get_promotions(self, state, payload): pass
        async def show_cart(self, state, payload): pass
        async def update_cart_item(self, state, payload): pass
        async def clear_cart(self, state, payload): pass
        async def check_availability(self, state, payload): pass
        async def get_order_status(self, state, payload): pass
        
    tools = DummyTools()
    register_all_tools(tools)
    
    assert len(TOOL_REGISTRY) >= 13
    
    expected_models = {
        "search": SearchProductsPayload,
        "explore_category": ExploreCategoryPayload,
        "search_products": SearchProductsPayload,
        "get_details": GetProductDetailsPayload,
        "add_to_cart": AddCartItemPayload,
        "remove_cart": RemoveCartItemPayload,
        "show_cart": ShowCartPayload,
        "checkout": PreviewCheckoutPayload,
        "place_order": PlaceOrderPayload,
        "get_promotions": GetPromotionsPayload,
        "update_cart_item": UpdateCartItemPayload,
        "clear_cart": ClearCartPayload,
        "check_availability": CheckAvailabilityPayload,
        "get_order_status": GetOrderStatusPayload
    }
    
    for name, model in expected_models.items():
        spec = TOOL_REGISTRY[name]
        assert spec.payload_model is model

@pytest.mark.asyncio
async def test_checker():
    # Re-register tools
    TOOL_REGISTRY.clear()
    class DummyTools:
        async def search(self, state, payload): pass
        async def search(self, state, payload): pass
        async def get_details(self, payload, state): pass
        async def add_to_cart(self, state, payload): pass
        async def remove_cart(self, state, payload): pass
        async def checkout(self, state): pass
        async def place_order(self, state, payload): pass
        async def get_promotions(self, state, payload): pass
        async def show_cart(self, state, payload): pass
        async def update_cart_item(self, state, payload): pass
        async def clear_cart(self, state, payload): pass
        async def check_availability(self, state, payload): pass
        async def get_order_status(self, state, payload): pass
    register_all_tools(DummyTools())
    
    state = ConversationState(session_id="test")
    
    # Test 1: place_order (No soft_required, multiple required fields)
    spec_place_order = TOOL_REGISTRY["place_order"]
    # Missing fields
    args = {"customer_name": "John Doe", "phone": "123"}
    error = await ParameterRequirementsChecker.check(spec_place_order, args, state)
    assert error == "MISSING PARAMETERS for place_order: delivery_address, city. INSTRUCTION: Ask the customer for delivery_address, city before proceeding with place_order."
    
    # All fields present
    args = {"customer_name": "John", "phone": "123", "delivery_address": "123 Main", "city": "NYC"}
    error = await ParameterRequirementsChecker.check(spec_place_order, args, state)
    assert error is None
    
    # Test 2: add_to_cart (Has soft_required)
    spec_add_cart = TOOL_REGISTRY["add_to_cart"]
    
    # quantity is required, product_id is soft_required. wait, product_id is NOT strictly required by Pydantic model (Optional), but soft_required resolver will run. 
    # the generic checker ONLY checks field_info.is_required() which is quantity.
    args = {"quantity": 1}
    error = await ParameterRequirementsChecker.check(spec_add_cart, args, state)
    assert error is None # Because quantity is present and it's the only required field
    
    # Test missing category_name for search
    spec_explore = TOOL_REGISTRY["explore_category"]
    args = {}
    error = await ParameterRequirementsChecker.check(spec_explore, args, state)
    assert error == "MISSING PARAMETERS for explore_category: category_name. INSTRUCTION: Ask the customer for category_name before proceeding with explore_category."
    
    # Test soft_required resolution
    state.selected_product_id = 99
    args = {"quantity": 1}
    await ParameterRequirementsChecker.check(spec_add_cart, args, state)
    assert args.get("product_id") == 99

