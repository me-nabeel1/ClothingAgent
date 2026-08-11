"""Agent-facing tool contracts for semantic interactions with the backend."""

import logging
from typing import Optional

from app.agent.state import ConversationState
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import (
    ProductSearchRequest,
    ProductSearchResponse,
    ProductDetails,
    AddCartItemRequest,
    CartView,
    PreviewCartRequest,
    StoreOrderPreview,
    PlaceOrderRequest,
    OrderView,
)

logger = logging.getLogger(__name__)


class AgentTools:
    """Agent tool layer providing semantic capabilities over the raw REST client."""

    def __init__(self, client: ClothingAppClient) -> None:
        self._client = client

    async def get_products(
        self,
        state: ConversationState,
        search_query: Optional[str] = None
    ) -> ProductSearchResponse:
        """Search products based on the current conversational state and query."""
        
        # Merge persistent preferences with temporary overrides
        categories = state.current_search.get("categories", state.categories)
        product_types = state.current_search.get("product_types", state.product_types)
        occasions = state.current_search.get("occasions", state.occasions)
        preferred_colors = state.current_search.get("preferred_colors", state.preferred_colors)
        excluded_colors = state.current_search.get("excluded_colors", state.excluded_colors)
        materials = state.current_search.get("materials", state.materials)
        fits = state.current_search.get("fits", state.fits)
        branch_preference = state.current_search.get("branch_preference", state.branch_preference)
        
        budget_min = state.budget.minimum
        budget_max = state.budget.maximum
        if "budget" in state.current_search:
            temp_budget = state.current_search["budget"]
            budget_min = temp_budget.get("minimum", budget_min)
            budget_max = temp_budget.get("maximum", budget_max)
            
        size_preferences = list(state.size_preferences.values())
        if "size_preferences" in state.current_search:
            size_preferences = list(state.current_search["size_preferences"].values())
            
        limit = 4 if len(categories) <= 1 else 12  # Fetch more if multiple categories
        
        # Ensure we never request more than 20 items per the prompt constraints
        limit = min(limit, 20)

        request = ProductSearchRequest(
            query_text=search_query,
            categories=categories,
            product_types=product_types,
            occasions=occasions,
            colors=preferred_colors,
            excluded_colors=excluded_colors,
            sizes=size_preferences,
            materials=materials,
            fits=fits,
            minimum_price=budget_min,
            maximum_price=budget_max,
            branch_code=branch_preference,
            in_stock_only=True,
            limit=limit,
            article_code=state.current_search.get("specific_article"),
        )

        logger.info(
            "agent_tool_get_products",
            extra={"event": "agent_tool_get_products", "filters": request.model_dump(exclude_defaults=True)},
        )

        response = await self._client.search_products(request)
        
        # Keep track of what we displayed
        state.record_displayed_products(response.products)
        return response

    async def get_product_details(self, product_id: int) -> ProductDetails:
        """Retrieve complete product details for an exact product."""
        
        logger.info(
            "agent_tool_get_product_details",
            extra={"event": "agent_tool_get_product_details", "product_id": product_id},
        )
        return await self._client.get_product(product_id)
        
    async def get_product_details_by_index(
        self, 
        index: int, 
        state: ConversationState
    ) -> Optional[ProductDetails]:
        """Retrieve complete product details based on conversational index."""
        if index < 1 or index > len(state.displayed_products):
            logger.warning("agent_tool_invalid_product_index", extra={"event": "invalid_product_index", "index": index})
            return None
            
        product_id = state.displayed_products[index - 1].product_id
        return await self.get_product_details(product_id)

    async def _ensure_cart(self, state: ConversationState) -> None:
        """Create a cart for the session if it doesn't exist."""
        if not state.cart.cart_id:
            cart = await self._client.create_cart()
            state.cart.cart_id = cart.cart_id
            state.cart.item_count = cart.total_quantity
            state.cart.subtotal = float(cart.subtotal)

    async def add_cart_item(self, state: ConversationState, variant_id: int, branch_id: int, quantity: int = 1) -> CartView:
        await self._ensure_cart(state)
        req = AddCartItemRequest(variant_id=variant_id, branch_id=branch_id, quantity=quantity)
        cart = await self._client.add_cart_item(state.cart.cart_id, req)
        state.cart.item_count = cart.total_quantity
        state.cart.subtotal = float(cart.subtotal)
        return cart

    async def preview_checkout(self, state: ConversationState, offer_code: Optional[str] = None) -> StoreOrderPreview | None:
        if not state.cart.cart_id:
            return None
        req = PreviewCartRequest(offer_code=offer_code)
        return await self._client.preview_cart(state.cart.cart_id, req)

    async def place_order(self, state: ConversationState, offer_code: Optional[str] = None) -> OrderView | None:
        if not state.cart.cart_id:
            return None
        req = PlaceOrderRequest(cart_id=state.cart.cart_id, offer_code=offer_code)
        order = await self._client.place_order(req)
        # Clear cart state after successful order
        state.cart.cart_id = None
        state.cart.item_count = 0
        state.cart.subtotal = 0.0
        return order
