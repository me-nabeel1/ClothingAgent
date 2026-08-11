"""Behavioral tests covering real conversational scenarios for V1 Runtime Hardening."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock

from app.agent.state import ConversationState, Budget
from app.agent.intent import IntentExtractor, StructuredIntent, ExtractedFilters, DeliveryInfoExtraction
from app.agent.tools import AgentTools
from app.agent.agent import SingleAgent
from app.clients.clothing_app.schemas import (
    StoreContext, ProductSearchResponse, ProductView, ProductDetails, 
    VariantView, BranchView, BranchAvailabilityView, CartView, StoreOrderPreview, OrderView
)
from datetime import datetime
from uuid import uuid4

# Setup reusable mock product
def _make_mock_product(pid: int = 1, art="NS-SH-001", name="Premium Oxford Shirt", 
                       cat="Shirts", ptype="shirt", occ="formal", price="4500", col="Black", sz="L", avail=True):
    return ProductView(
        product_id=pid, article_code=art, product_name=name, category=cat, product_type=ptype,
        gender="MEN", brand="Northstar", occasion=occ, base_price=Decimal(price), final_price=Decimal(price),
        variants=[VariantView(
            variant_id=pid*10, sku=f"{art}-{col[:1]}-{sz}", color=col, size=sz, price=Decimal(price),
            final_price=Decimal(price), is_available=avail,
            branch_availability=[BranchAvailabilityView(branch_id=1, branch_code="ISB", branch_name="Islamabad", is_available=avail, available_quantity=5 if avail else 0)]
        )]
    )

@pytest.fixture
def store_context() -> StoreContext:
    return StoreContext(
        store_name="Northstar Menswear", store_id="northstar",
        branches=[BranchView(branch_id=1, branch_code="ISB", branch_name="Islamabad", city="Islamabad", address="F-7 Markaz")],
        categories=["Shirts", "Pants", "Outerwear", "Traditional"],
        subcategories=[], product_types=["shirt", "pants", "hoodie", "jacket"],
        supported_attributes=[], sizes=["S", "M", "L", "XL"], colors=["Black", "White", "Navy"],
        seasons=["Summer", "Winter"], occasions=["wedding", "casual", "formal"],
        capabilities=["search", "cart", "checkout"]
    )

@pytest.fixture
def mock_llm() -> AsyncMock:
    llm = AsyncMock()
    async def mock_generate_text(messages, **kwargs):
        return str(messages)
    llm.generate_text = AsyncMock(side_effect=mock_generate_text)
    llm.configured = True
    return llm

@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock()
    client.search_products.return_value = ProductSearchResponse(products=[_make_mock_product()], result_count=1)
    client.get_product.return_value = ProductDetails(product=_make_mock_product())
    from uuid import uuid4
    cart_id = uuid4()
    client.create_cart.return_value = CartView(cart_id=cart_id, created_at=datetime.now(), updated_at=datetime.now(), expires_at=datetime.now())
    client.add_cart_item.return_value = CartView(cart_id=cart_id, total_quantity=1, subtotal=Decimal("4500.00"), created_at=datetime.now(), updated_at=datetime.now(), expires_at=datetime.now())
    client.preview_cart.return_value = StoreOrderPreview(cart_id=cart_id, grand_total=Decimal("4500.00"))
    client.place_order.return_value = OrderView(
        order_id=uuid4(), order_number="ORD-123", status="PLACED", subtotal=Decimal("4500.00"), discount_total=Decimal("0"),
        delivery_fee=Decimal("0"), grand_total=Decimal("4500.00"), applied_offer_code=None, customer_name="John Doe", phone="555-1234",
        delivery_address="123 Main St", city="Islamabad", delivery_notes="", created_at=datetime.now()
    )
    return client

class TestBehavioralScenarios:
    
    @pytest.mark.asyncio
    async def test_scenario_1_broad_search(self, mock_llm, mock_client, store_context):
        """Scenario 1 - Broad search: 'I need something for a wedding.'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s1")
        
        extractor.extract.return_value = StructuredIntent(
            intent="search", filters=ExtractedFilters(occasions=["wedding"])
        )
        
        await agent.process_message("I need something for a wedding.", state, store_context)
        
        # Verify the intent extraction sets the state properly and searches
        assert state.occasions == ["wedding"]
        mock_client.search_products.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_scenario_2_refinement(self, mock_llm, mock_client, store_context):
        """Scenario 2 - Refinement: Wedding clothes -> black ones -> size L."""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s2")
        
        # 1. Broad
        extractor.extract.return_value = StructuredIntent(intent="search", filters=ExtractedFilters(occasions=["wedding"]))
        await agent.process_message("I need wedding clothes.", state, store_context)
        assert state.occasions == ["wedding"]
        
        # 2. Refine color
        extractor.extract.return_value = StructuredIntent(intent="search", filters=ExtractedFilters(colors=["Black"]))
        await agent.process_message("Show me black ones.", state, store_context)
        assert state.occasions == ["wedding"]
        assert state.preferred_colors == ["Black"]
        
        # 3. Refine size
        extractor.extract.return_value = StructuredIntent(intent="search", filters=ExtractedFilters(sizes={"Shirts": "L"}))
        await agent.process_message("Size L.", state, store_context)
        assert state.occasions == ["wedding"]
        assert state.preferred_colors == ["Black"]
        assert state.size_preferences == {"Shirts": "L"}
        
    @pytest.mark.asyncio
    async def test_scenario_3_multi_category(self, mock_llm, mock_client, store_context):
        """Scenario 3 - Multiple categories: 'Show me hoodies and jackets.'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s3")
        
        extractor.extract.return_value = StructuredIntent(
            intent="search", filters=ExtractedFilters(categories=["Outerwear"], product_types=["hoodie", "jacket"])
        )
        await agent.process_message("Show me hoodies and jackets.", state, store_context)
        assert state.product_types == ["hoodie", "jacket"]
        mock_client.search_products.assert_called_once()

    @pytest.mark.asyncio
    async def test_scenario_4_exact_unavailable(self, mock_llm, mock_client, store_context):
        """Scenario 4 - Exact unavailable article: 'Do you have NS-XXX?'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s4")
        
        mock_client.search_products.return_value = ProductSearchResponse(products=[_make_mock_product(avail=False)], result_count=1)
        
        extractor.extract.return_value = StructuredIntent(
            intent="search", search_overrides=ExtractedFilters(specific_article="NS-XXX")
        )
        response = await agent.process_message("Do you have NS-XXX?", state, store_context)
    
        assert state.current_search.get("specific_article") == "NS-XXX"
        # Mock LLM generates response based on the search_products result
        # Our mock LLM just returns the stringified messages, so we check if the message contains the availability state
        assert "Out of Stock" in response
        
    @pytest.mark.asyncio
    async def test_scenario_5_product_detail(self, mock_llm, mock_client, store_context):
        """Scenario 5 - Product detail: 'Tell me more about product 1.'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s5")
        
        state.record_displayed_products([_make_mock_product()])
        extractor.extract.return_value = StructuredIntent(intent="get_details", selected_product_index=1)
        
        response = await agent.process_message("Tell me more about product 1.", state, store_context)
        mock_client.get_product.assert_called_once_with(1)
        
        # Verify concise format
        assert "Product Details for" in response
        assert "Material:" in response
        
    @pytest.mark.asyncio
    async def test_scenario_6_cart(self, mock_llm, mock_client, store_context):
        """Scenario 6 - Cart: 'Add product 1.'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s6")
        state.record_displayed_products([_make_mock_product()])
        state.selected_product_id = 1
        
        extractor.extract.return_value = StructuredIntent(intent="add_to_cart", filters=ExtractedFilters(sizes={"Shirts": "L"}))
        await agent.process_message("Add product 1.", state, store_context)
        mock_client.add_cart_item.assert_called_once()
        assert state.cart.item_count == 1
        
    @pytest.mark.asyncio
    async def test_scenario_7_checkout(self, mock_llm, mock_client, store_context):
        """Scenario 7 - Checkout: 'Checkout.'"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s7")
        state.cart.cart_id = uuid4()
        
        extractor.extract.return_value = StructuredIntent(intent="checkout")
        await agent.process_message("Checkout.", state, store_context)
        mock_client.preview_cart.assert_called_once()

    @pytest.mark.asyncio
    async def test_scenario_8_missing_delivery(self, mock_llm, mock_client, store_context):
        """Scenario 8 - Missing delivery information"""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s8")
        state.cart.cart_id = uuid4()
        
        extractor.extract.return_value = StructuredIntent(intent="place_order", order_confirmed=True)
        response = await agent.process_message("Place order.", state, store_context)
        
        assert "Missing delivery information" in response
        mock_client.place_order.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_scenario_9_confirmation(self, mock_llm, mock_client, store_context):
        """Scenario 9 - Confirmation: Only after explicit confirmation does place_order execute."""
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=AgentTools(mock_client))
        state = ConversationState(session_id="s9")
        state.cart.cart_id = uuid4()
        
        # Give full info
        extractor.extract.return_value = StructuredIntent(
            intent="place_order", order_confirmed=True,
            delivery_info=DeliveryInfoExtraction(customer_name="A", phone="B", delivery_address="C", city="D")
        )
        response = await agent.process_message("Place it.", state, store_context)
        
        mock_client.place_order.assert_called_once()
        assert "Order placed successfully" in response
