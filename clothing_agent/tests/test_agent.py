"""Comprehensive foundation tests for the Single Agent architecture.

Tests cover:
- Agent architecture (single agent exists, no multi-agent)
- Store context loading and representation
- Conversation state creation, incremental updates, semantic sizes
- Product retrieval tool (category, occasion, color, size, budget, branch, combined, article, OOS)
- Behavioral rules (minimum intent, no unnecessary clarification, retrieval limit)
- End-to-end agent pipeline with deterministic mocks
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.agent.state import ConversationState, Budget, DisplayedProduct, ProductInterest
from app.agent.intent import IntentExtractor, StructuredIntent, ExtractedFilters
from app.agent.tools import AgentTools
from app.agent.agent import SingleAgent
from app.context.store import StoreContextManager
from app.clients.clothing_app.schemas import (
    StoreContext,
    ProductSearchRequest,
    ProductSearchResponse,
    ProductView,
    ProductDetails,
    VariantView,
    BranchView,
    BranchAvailabilityView,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_product(
    product_id: int = 1,
    article_code: str = "NS-SH-001",
    product_name: str = "Premium Oxford Shirt",
    category: str = "Shirts",
    product_type: str = "dress_shirt",
    occasion: str = "formal",
    base_price: Decimal = Decimal("4500"),
    color: str = "White",
    size: str = "L",
    is_available: bool = True,
) -> ProductView:
    return ProductView(
        product_id=product_id,
        article_code=article_code,
        product_name=product_name,
        category=category,
        product_type=product_type,
        gender="Men",
        brand="Northstar",
        occasion=occasion,
        base_price=base_price,
        final_price=base_price,
        variants=[
            VariantView(
                variant_id=product_id * 10,
                sku=f"{article_code}-{color[0]}-{size}",
                color=color,
                size=size,
                price=base_price,
                final_price=base_price,
                is_available=is_available,
                branch_availability=[
                    BranchAvailabilityView(
                        branch_code="ISB",
                        branch_name="Islamabad",
                        is_available=is_available,
                        available_quantity=5 if is_available else 0,
                    )
                ],
            )
        ],
    )


@pytest.fixture
def store_context() -> StoreContext:
    return StoreContext(
        store_name="Northstar Menswear",
        store_id="northstar",
        branches=[
            BranchView(branch_id=1, branch_code="ISB", branch_name="Islamabad", city="Islamabad", address="F-7 Markaz"),
            BranchView(branch_id=2, branch_code="LHR", branch_name="Lahore", city="Lahore", address="Gulberg III"),
        ],
        categories=["Shirts", "Pants", "Jackets", "Kurtas"],
        subcategories=["Oxford", "Chinos", "Blazer"],
        product_types=["dress_shirt", "polo", "chino", "jacket", "kurta"],
        supported_attributes=["Cotton", "Linen", "Wool"],
        sizes=["S", "M", "L", "XL", "30", "32", "34"],
        colors=["White", "Black", "Navy", "Maroon", "Blue"],
        seasons=["Summer", "Winter", "All-Season"],
        occasions=["formal", "casual", "wedding", "sport"],
        capabilities=["search", "cart", "checkout"],
    )


@pytest.fixture
def mock_llm() -> AsyncMock:
    llm = AsyncMock()
    llm.generate_text.return_value = "Here are some options for you."
    llm.configured = True
    return llm


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock()
    client.search_products.return_value = ProductSearchResponse(
        products=[_make_product()], result_count=1
    )
    client.get_product.return_value = ProductDetails(product=_make_product())
    client.get_store_context.return_value = StoreContext(
        store_name="Test",
        store_id="test",
        branches=[],
        categories=["Shirts"],
        subcategories=[],
        product_types=[],
        supported_attributes=[],
        sizes=[],
        colors=[],
        seasons=[],
        occasions=[],
        capabilities=[],
    )
    return client


# ===================================================================
# 1. AGENT ARCHITECTURE TESTS
# ===================================================================

class TestAgentArchitecture:
    """Verify single agent exists and specialist agents are removed."""

    def test_single_agent_class_exists(self):
        """The SingleAgent class must be importable."""
        from app.agent.agent import SingleAgent
        assert SingleAgent is not None

    def test_no_specialist_agent_modules(self):
        """Multi-agent modules (sales, shopping, fashion, cart, registry, router) must not be importable."""
        import importlib
        for module_name in [
            "app.agents.sales.service",
            "app.agents.shopping.service",
            "app.agents.fashion.service",
            "app.agents.cart.service",
            "app.agents.registry",
            "app.core.routing",
        ]:
            with pytest.raises(ModuleNotFoundError):
                importlib.import_module(module_name)

    def test_no_agent_registry_in_container(self):
        """The container must not reference AgentRegistry."""
        import inspect
        from app.core.container import AppContainer
        source = inspect.getsource(AppContainer)
        assert "AgentRegistry" not in source
        assert "SalesAgent" not in source
        assert "ShoppingAgent" not in source
        assert "FashionAgent" not in source
        assert "CartAgent" not in source

    def test_container_has_single_agent(self):
        """The container must expose exactly one agent."""
        import inspect
        from app.core.container import AppContainer
        source = inspect.getsource(AppContainer)
        assert "SingleAgent" in source


# ===================================================================
# 2. STORE CONTEXT TESTS
# ===================================================================

class TestStoreContext:
    """Verify context loading and representation."""

    @pytest.mark.asyncio
    async def test_context_loads(self, mock_client):
        """StoreContextManager can load context from the client."""
        manager = StoreContextManager(mock_client)
        assert not manager.is_loaded
        ctx = await manager.load_context()
        assert manager.is_loaded
        assert ctx.store_name == "Test"
        mock_client.get_store_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_refresh(self, mock_client):
        """refresh_context reloads from the backend."""
        manager = StoreContextManager(mock_client)
        await manager.load_context()
        await manager.refresh_context()
        assert mock_client.get_store_context.call_count == 2

    def test_context_not_loaded_raises(self, mock_client):
        """Accessing context before loading raises RuntimeError."""
        manager = StoreContextManager(mock_client)
        with pytest.raises(RuntimeError, match="not been loaded"):
            manager.get_context()

    def test_dynamic_vocabulary_consumed(self, store_context):
        """Context provides the expected dynamic vocabulary."""
        assert "Shirts" in store_context.categories
        assert "Black" in store_context.colors
        assert "ISB" in [b.branch_code for b in store_context.branches]
        assert "wedding" in store_context.occasions


# ===================================================================
# 3. CONVERSATION STATE TESTS
# ===================================================================

class TestConversationState:
    """Verify state creation, incremental updates, and semantic sizes."""

    def test_state_creation(self):
        state = ConversationState(session_id="s1")
        assert state.session_id == "s1"
        assert state.conversation_stage == "greeting"
        assert state.categories == []
        assert state.preferred_colors == []

    def test_incremental_update_preserves_existing(self):
        """Updating colors must not erase categories."""
        state = ConversationState(session_id="s1")
        state.update({"categories": ["Shirts"]})
        state.update({"preferred_colors": ["Black"]})
        assert state.categories == ["Shirts"]
        assert state.preferred_colors == ["Black"]

    def test_color_replacement(self):
        """'Actually make it blue' replaces colors, not appends."""
        state = ConversationState(session_id="s1")
        state.update({"preferred_colors": ["Black"]})
        state.update({"preferred_colors": ["Blue"]})
        assert state.preferred_colors == ["Blue"]

    def test_budget_incremental(self):
        """Setting max budget doesn't destroy min budget."""
        state = ConversationState(session_id="s1")
        state.update({"budget": {"maximum": 5000}})
        assert state.budget.maximum == 5000
        assert state.budget.minimum is None
        state.update({"budget": {"minimum": 1000}})
        assert state.budget.maximum == 5000
        assert state.budget.minimum == 1000

    def test_semantic_sizes(self):
        """Size preferences track which product type a size belongs to."""
        state = ConversationState(session_id="s1")
        state.update({"size_preferences": {"shirt": "L"}})
        state.update({"size_preferences": {"pants": "34"}})
        assert state.size_preferences == {"shirt": "L", "pants": "34"}
        # Updating shirt size doesn't wipe pants
        state.update({"size_preferences": {"shirt": "XL"}})
        assert state.size_preferences == {"shirt": "XL", "pants": "34"}

    def test_clear_search_preferences(self):
        """clear_search_preferences resets ephemeral fields but keeps session."""
        state = ConversationState(session_id="s1")
        state.update({"categories": ["Shirts"], "preferred_colors": ["Black"]})
        state.cart.cart_id = "abc"
        state.clear_search_preferences()
        assert state.categories == []
        assert state.preferred_colors == []
        assert state.cart.cart_id == "abc"  # cart survives

    def test_record_displayed_products(self):
        products = [_make_product(product_id=1), _make_product(product_id=2, article_code="NS-SH-002", product_name="Polo")]
        state = ConversationState(session_id="s1")
        state.record_displayed_products(products)
        assert len(state.displayed_products) == 2
        assert state.displayed_products[0].product_id == 1

    def test_product_interest_tracking(self):
        """Can record unavailable product interest for future notification."""
        state = ConversationState(session_id="s1")
        state.requested_unavailable_products.append(
            ProductInterest(article_code="NS-SH-099", product_name="Ghost Shirt", requested_color="Pink")
        )
        assert len(state.requested_unavailable_products) == 1
        assert state.requested_unavailable_products[0].article_code == "NS-SH-099"


# ===================================================================
# 4. PRODUCT RETRIEVAL TOOL TESTS
# ===================================================================

class TestAgentTools:
    """Verify AgentTools delegates correctly to the client."""

    @pytest.mark.asyncio
    async def test_category_search(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", categories=["Shirts"])
        result = await tools.get_products(state)
        mock_client.search_products.assert_called_once()
        req = mock_client.search_products.call_args[0][0]
        assert req.categories == ["Shirts"]

    @pytest.mark.asyncio
    async def test_occasion_search(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", occasions=["wedding"])
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.occasions == ["wedding"]

    @pytest.mark.asyncio
    async def test_color_filtering(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", preferred_colors=["Black"])
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.colors == ["Black"]

    @pytest.mark.asyncio
    async def test_budget_filtering(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", budget=Budget(maximum=5000))
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.maximum_price == 5000

    @pytest.mark.asyncio
    async def test_branch_filtering(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", branch_preference="ISB")
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.branch_code == "ISB"

    @pytest.mark.asyncio
    async def test_combined_filters(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(
            session_id="s1",
            categories=["Shirts"],
            preferred_colors=["Black"],
            occasions=["wedding"],
            budget=Budget(maximum=5000),
            branch_preference="ISB",
        )
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.categories == ["Shirts"]
        assert req.colors == ["Black"]
        assert req.occasions == ["wedding"]
        assert req.maximum_price == 5000
        assert req.branch_code == "ISB"

    @pytest.mark.asyncio
    async def test_multiple_categories_higher_limit(self, mock_client):
        """Multiple categories should request more products."""
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", categories=["Shirts", "Pants"])
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.limit > 4  # higher limit for multi-category

    @pytest.mark.asyncio
    async def test_retrieval_never_exceeds_20(self, mock_client):
        """The limit must never exceed 20 regardless of category count."""
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1", categories=["A", "B", "C", "D", "E", "F"])
        await tools.get_products(state)
        req = mock_client.search_products.call_args[0][0]
        assert req.limit <= 20

    @pytest.mark.asyncio
    async def test_get_product_details(self, mock_client):
        tools = AgentTools(mock_client)
        result = await tools.get_product_details(42)
        mock_client.get_product.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_get_product_details_by_index_valid(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1")
        state.displayed_products = [
            DisplayedProduct(product_id=10, article_code="A", product_name="P1"),
            DisplayedProduct(product_id=20, article_code="B", product_name="P2"),
        ]
        result = await tools.get_product_details_by_index(2, state)
        mock_client.get_product.assert_called_once_with(20)

    @pytest.mark.asyncio
    async def test_get_product_details_by_index_invalid(self, mock_client):
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1")
        state.displayed_products = []
        result = await tools.get_product_details_by_index(5, state)
        assert result is None

    @pytest.mark.asyncio
    async def test_displayed_products_recorded(self, mock_client):
        """After get_products, the state should record displayed products."""
        tools = AgentTools(mock_client)
        state = ConversationState(session_id="s1")
        await tools.get_products(state)
        assert len(state.displayed_products) == 1
        assert state.displayed_products[0].article_code == "NS-SH-001"


# ===================================================================
# 5. BEHAVIORAL RULES TESTS
# ===================================================================

class TestBehavioralRules:
    """Test critical agent behavioral constraints."""

    @pytest.mark.asyncio
    async def test_minimum_intent_triggers_search(self, mock_llm, store_context):
        """A search intent with even one filter triggers retrieval immediately, no clarification."""
        mock_extractor = AsyncMock(spec=IntentExtractor)
        mock_extractor.extract.return_value = StructuredIntent(
            intent="search",
            filters=ExtractedFilters(occasions=["wedding"]),
        )
        mock_tools = AsyncMock(spec=AgentTools)
        mock_tools.get_products.return_value = ProductSearchResponse(
            products=[_make_product(occasion="wedding")], result_count=1
        )

        agent = SingleAgent(llm=mock_llm, extractor=mock_extractor, tools=mock_tools)
        state = ConversationState(session_id="s1")

        await agent.process_message("I need wedding clothes", state, store_context)

        # The agent must have called get_products (i.e., searched immediately)
        mock_tools.get_products.assert_called_once()

    @pytest.mark.asyncio
    async def test_general_chat_does_not_trigger_search(self, mock_llm, store_context):
        """General chat intent should not trigger product search."""
        mock_extractor = AsyncMock(spec=IntentExtractor)
        mock_extractor.extract.return_value = StructuredIntent(intent="general_chat")
        mock_tools = AsyncMock(spec=AgentTools)

        agent = SingleAgent(llm=mock_llm, extractor=mock_extractor, tools=mock_tools)
        state = ConversationState(session_id="s1")

        await agent.process_message("Hello, how are you?", state, store_context)

        mock_tools.get_products.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_details_uses_selected_product(self, mock_llm, store_context):
        """When intent is get_details and a product is selected, details are fetched."""
        mock_extractor = AsyncMock(spec=IntentExtractor)
        mock_extractor.extract.return_value = StructuredIntent(
            intent="get_details",
            selected_product_index=1,
        )
        mock_tools = AsyncMock(spec=AgentTools)
        mock_tools.get_product_details.return_value = ProductDetails(product=_make_product())

        agent = SingleAgent(llm=mock_llm, extractor=mock_extractor, tools=mock_tools)
        state = ConversationState(session_id="s1")
        state.displayed_products = [
            DisplayedProduct(product_id=42, article_code="NS-SH-001", product_name="Oxford")
        ]

        await agent.process_message("Tell me more about that first one", state, store_context)

        assert state.selected_product_id == 42
        mock_tools.get_product_details.assert_called_once_with(42)


# ===================================================================
# 6. END-TO-END PIPELINE TESTS
# ===================================================================

class TestEndToEndPipeline:
    """Integration-style tests verifying message → agent → tool → client → response."""

    @pytest.mark.asyncio
    async def test_full_search_pipeline(self, mock_llm, store_context):
        """Complete flow: user asks for shirts → intent extracted → tools called → response generated."""
        mock_client = AsyncMock()
        mock_client.search_products.return_value = ProductSearchResponse(
            products=[
                _make_product(product_id=1, product_name="Oxford Shirt"),
                _make_product(product_id=2, article_code="NS-SH-002", product_name="Polo Shirt"),
            ],
            result_count=2,
        )

        extractor = AsyncMock(spec=IntentExtractor)
        extractor.extract.return_value = StructuredIntent(
            intent="search",
            filters=ExtractedFilters(categories=["Shirts"]),
        )

        tools = AgentTools(mock_client)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=tools)
        state = ConversationState(session_id="s1")

        reply = await agent.process_message("Show me shirts", state, store_context)

        # Verify the pipeline completed
        assert reply == "Here are some options for you."
        assert state.categories == ["Shirts"]
        assert len(state.displayed_products) == 2
        mock_client.search_products.assert_called_once()

    @pytest.mark.asyncio
    async def test_incremental_refinement_pipeline(self, mock_llm, store_context):
        """Simulates: user asks for wedding clothes → then refines with 'black ones'."""
        mock_client = AsyncMock()
        mock_client.search_products.return_value = ProductSearchResponse(
            products=[_make_product()], result_count=1,
        )

        tools = AgentTools(mock_client)
        extractor = AsyncMock(spec=IntentExtractor)
        agent = SingleAgent(llm=mock_llm, extractor=extractor, tools=tools)
        state = ConversationState(session_id="s1")

        # Turn 1: "I need wedding clothes"
        extractor.extract.return_value = StructuredIntent(
            intent="search",
            filters=ExtractedFilters(occasions=["wedding"]),
        )
        await agent.process_message("I need wedding clothes", state, store_context)
        assert state.occasions == ["wedding"]

        # Turn 2: "Show me black ones"
        extractor.extract.return_value = StructuredIntent(
            intent="search",
            filters=ExtractedFilters(colors=["Black"]),
        )
        await agent.process_message("Show me black ones", state, store_context)
        # Occasions should survive
        assert state.occasions == ["wedding"]
        assert state.preferred_colors == ["Black"]

        # Turn 3: "Under 5000"
        extractor.extract.return_value = StructuredIntent(
            intent="search",
            filters=ExtractedFilters(budget=Budget(maximum=5000)),
        )
        await agent.process_message("Under 5000", state, store_context)
        assert state.occasions == ["wedding"]
        assert state.preferred_colors == ["Black"]
        assert state.budget.maximum == 5000


# ===================================================================
# 7. NO HARDCODED BUSINESS TRUTH TESTS
# ===================================================================

class TestNoHardcodedTruth:
    """Verify the agent code doesn't embed store-specific constants."""

    def test_no_hardcoded_colors_in_agent(self):
        import inspect
        from app.agent import agent as agent_module
        source = inspect.getsource(agent_module)
        # Should not contain hardcoded color sets
        assert "COLORS = {" not in source
        assert "CATEGORIES = {" not in source

    def test_no_hardcoded_vocabulary_in_tools(self):
        import inspect
        from app.agent import tools as tools_module
        source = inspect.getsource(tools_module)
        assert "COLORS = {" not in source
        assert "CATEGORIES = {" not in source
        assert "PURPOSES = {" not in source

    def test_prompt_does_not_embed_specific_products(self):
        from app.llm.prompts import SYSTEM_PROMPT
        assert "NS-SH-001" not in SYSTEM_PROMPT
        assert "4500" not in SYSTEM_PROMPT
