"""Agent-facing tool contracts for semantic interactions with the backend."""

import logging
from typing import Optional

from app.agent.state import ConversationState
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import (
    ProductSearchRequest,
    ProductSearchResponse,
    ProductDetails,
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
        
        limit = 4 if len(state.categories) <= 1 else 12  # Fetch more if multiple categories
        
        # Ensure we never request more than 20 items per the prompt constraints
        limit = min(limit, 20)

        request = ProductSearchRequest(
            query_text=search_query,
            categories=state.categories,
            product_types=state.product_types,
            occasions=state.occasions,
            colors=state.preferred_colors,
            excluded_colors=state.excluded_colors,
            sizes=list(state.size_preferences.values()),
            materials=state.materials,
            fits=state.fits,
            minimum_price=state.budget.minimum,
            maximum_price=state.budget.maximum,
            branch_code=state.branch_preference,
            in_stock_only=True,
            limit=limit,
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
