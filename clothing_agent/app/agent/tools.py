"""Agent-facing tool contracts for semantic interactions with the backend."""

import logging
from typing import Optional, Any

from app.agent.state import ConversationState, CartItemContext
from app.agent.schemas import (
    ExploreCategoryPayload,
    SearchProductsPayload,
    GetProductDetailsPayload,
    AddCartItemPayload,
    RemoveCartItemPayload,
    PlaceOrderPayload
)
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


import re

def normalize_category_name(raw: str) -> str:
    raw_lower = raw.strip().lower()
    if raw_lower in ["all", "all products", "everything", "catalog"]:
        return ""
    if "t-shirt" in raw_lower or "tshirt" in raw_lower or "t shirt" in raw_lower or "tee" in raw_lower:
        return "T-Shirts"
    elif "polo" in raw_lower:
        return "Polo Shirts"
    elif "shirt" in raw_lower:
        return "Shirts"
    elif "trouser" in raw_lower:
        return "Trousers"
    elif "pant" in raw_lower:
        return "Pants"
    elif "hoodie" in raw_lower or "jacket" in raw_lower or "outerwear" in raw_lower:
        return "Outerwear"
    elif "traditional" in raw_lower or "kurta" in raw_lower:
        return "Traditional"
    elif "jean" in raw_lower:
        return "Jeans"
    return raw.strip().title()

def parse_categories_from_input(categories: Any = None, search_query: Optional[str] = None) -> list[str]:
    raw_items: list[str] = []
    if isinstance(categories, list):
        for item in categories:
            if isinstance(item, str):
                parts = re.split(r",|\band\b|&", item, flags=re.IGNORECASE)
                raw_items.extend(parts)
    elif isinstance(categories, str):
        parts = re.split(r",|\band\b|&", categories, flags=re.IGNORECASE)
        raw_items.extend(parts)

    if not raw_items and search_query:
        sq_lower = search_query.lower()
        if "t-shirt" in sq_lower or "tshirt" in sq_lower or "t shirt" in sq_lower or "tee" in sq_lower:
            raw_items.append("T-Shirts")
        elif "shirt" in sq_lower:
            raw_items.append("Shirts")
        if "trouser" in sq_lower:
            raw_items.append("Trousers")
        if "pant" in sq_lower:
            raw_items.append("Pants")
        if "hoodie" in sq_lower or "jacket" in sq_lower or "outerwear" in sq_lower:
            raw_items.append("Outerwear")
        if "traditional" in sq_lower or "kurta" in sq_lower:
            raw_items.append("Traditional")

    normalized: list[str] = []
    for raw in raw_items:
        clean = raw.strip()
        if clean:
            norm = normalize_category_name(clean)
            if norm and norm not in normalized:
                normalized.append(norm)
    return normalized


class AgentTools:
    """Agent tool layer providing semantic capabilities over the raw REST client."""

    def __init__(self, client: ClothingAppClient) -> None:
        self._client = client

    async def explore_category(
        self,
        state: ConversationState,
        payload: ExploreCategoryPayload
    ) -> ProductSearchResponse:
        """Explore single or multi-category requests, delegates to get_products."""
        cats = parse_categories_from_input(payload.category_name)
        search_payload = SearchProductsPayload(categories=cats)
        return await self.get_products(state, search_payload, limit_override=3)

    async def get_products(
        self,
        state: ConversationState,
        payload: Optional[SearchProductsPayload] = None,
        limit_override: Optional[int] = None
    ) -> ProductSearchResponse:
        """Search products using explicit parameters from the LLM tool call."""
        if payload is None:
            payload = SearchProductsPayload()
        
        if payload.clear_previous_preferences:
            state.clear_search_preferences()
            
        # Parse and set multi-category preferences if provided or inferred
        if payload.categories is not None:
            parsed = parse_categories_from_input(payload.categories, payload.search_query)
            if parsed:
                state.categories = parsed
        elif not state.categories and payload.search_query:
            parsed = parse_categories_from_input(None, payload.search_query)
            if parsed:
                state.categories = parsed

        if payload.product_types is not None: state.product_types = payload.product_types
        if payload.occasions is not None: state.occasions = payload.occasions
        if payload.colors is not None: state.preferred_colors = payload.colors
        if payload.excluded_colors is not None: state.excluded_colors = payload.excluded_colors
        if payload.materials is not None: state.materials = payload.materials
        if payload.fits is not None: state.fits = payload.fits
        if payload.seasons is not None: state.seasons = payload.seasons
        if payload.branch is not None: state.branch_preference = payload.branch
        if payload.sizes is not None:
            for k, v in payload.sizes.items():
                state.size_preferences[k] = v
        if payload.budget is not None:
            if payload.budget.minimum is not None: state.budget.minimum = payload.budget.minimum
            if payload.budget.maximum is not None: state.budget.maximum = payload.budget.maximum
            
        budget_min = state.budget.minimum
        budget_max = state.budget.maximum
        
        # If user asks for cheaper but provides no maximum, infer from currently displayed products
        if budget_max is None and state.displayed_products:
            min_displayed_price = min((p.price for p in state.displayed_products if p.price > 0), default=None)
            if min_displayed_price is not None:
                budget_max = float(min_displayed_price) - 0.01

        # Determine limit based on categories
        if limit_override is not None:
            limit = limit_override
        else:
            cats = state.categories or []
            limit = max(6, 3 * len(cats))
            limit = min(limit, 20)

        request = ProductSearchRequest(
            query_text=payload.search_query,
            categories=state.categories,
            product_types=state.product_types,
            occasions=state.occasions,
            colors=state.preferred_colors,
            excluded_colors=state.excluded_colors,
            size_mapping=state.size_preferences,
            excluded_product_ids=list(state.seen_product_ids),
            materials=state.materials,
            fits=state.fits,
            seasons=state.seasons,
            minimum_price=budget_min,
            maximum_price=budget_max,
            branch_code=state.branch_preference,
            in_stock_only=True,
            limit=limit * 3,  # Fetch extra to survive strict agent-side drops
            article_code=payload.specific_article,
        )

        logger.info(
            "agent_tool_get_products",
            extra={"event": "agent_tool_get_products", "filters": request.model_dump(exclude_defaults=True)},
        )

        response = await self._client.search_products(request)
        
        # Enforce strict category matching if categories were requested
        if state.categories and response.products:
            def _matches_category(p, requested_cats):
                cat_name = (p.category or "").lower()
                prod_name = (p.product_name or "").lower()
                prod_type = (p.product_type or "").lower()
                for req in requested_cats:
                    req_stem = req.lower().rstrip("s")
                    if req_stem in cat_name or req_stem in prod_name or req_stem in prod_type:
                        return True
                    if cat_name in req_stem or prod_type in req_stem:
                        return True
                return False

            matched = [p for p in response.products if _matches_category(p, state.categories)]
            response.products = matched[:limit] # Apply actual limit after strict filter
            response.result_count = len(response.products)
        else:
            response.products = response.products[:limit]
            response.result_count = len(response.products)

        # Keep track of what we displayed
        state.record_displayed_products(response.products)
        return response

    async def get_product_details(self, payload: GetProductDetailsPayload, state: ConversationState) -> Optional[ProductDetails]:
        """Retrieve complete product details for an exact product."""
        product_id = payload.product_id
        if not product_id and payload.selected_product_index is not None:
            index = payload.selected_product_index
            if index < 1 or index > len(state.displayed_products):
                logger.warning("agent_tool_invalid_product_index", extra={"event": "invalid_product_index", "index": index})
                return None
            product_id = state.displayed_products[index - 1].product_id
            
        if not product_id:
            return None
            
        logger.info(
            "agent_tool_get_product_details",
            extra={"event": "agent_tool_get_product_details", "product_id": product_id},
        )
        return await self._client.get_product(product_id)

    async def _ensure_cart(self, state: ConversationState) -> None:
        """Create a cart for the session if it doesn't exist."""
        if not state.cart.cart_id:
            cart = await self._client.create_cart()
            state.cart.cart_id = cart.cart_id
            state.cart.item_count = cart.total_quantity
            state.cart.subtotal = float(cart.subtotal)
            state.cart.items = []

    async def add_cart_item(self, state: ConversationState, payload: AddCartItemPayload) -> CartView | None:
        await self._ensure_cart(state)
        
        product_id = payload.product_id
        if not product_id and payload.selected_product_index is not None:
            index = payload.selected_product_index
            if 1 <= index <= len(state.displayed_products):
                product_id = state.displayed_products[index - 1].product_id
            
        if not product_id:
            product_id = state.selected_product_id

        if not product_id and state.displayed_products:
            product_id = state.displayed_products[0].product_id

        if product_id:
            state.selected_product_id = product_id
            
        if not product_id:
            return None
            
        details = await self._client.get_product(product_id)
        if not details or not details.product or not details.product.variants:
            return None

        # Determine available colors and sizes among in-stock variants
        in_stock_variants = [v for v in details.product.variants if v.is_available]
        if not in_stock_variants:
            in_stock_variants = details.product.variants

        available_colors = set(v.color for v in in_stock_variants)
        available_sizes = set(v.size for v in in_stock_variants)

        # Always require BOTH color and size to be explicitly specified in payload
        if not payload.color or not payload.size:
            logger.info("add_cart_item_missing_color_or_size", extra={"color": payload.color, "size": payload.size, "product_id": product_id})
            return None

        matching_variants = []
        for v in details.product.variants:
            if payload.color and v.color.lower() != payload.color.lower():
                continue
            if payload.size and v.size.lower() != payload.size.lower():
                continue
            matching_variants.append(v)
            
        if not matching_variants:
            return None
            
        variant = matching_variants[0]
        variant_id = variant.variant_id
        
        branch_id = None
        for a in variant.branch_availability:
            if a.is_available and a.available_quantity > 0:
                branch_id = a.branch_id
                break
                
        if not branch_id:
            return None # Out of stock

        req = AddCartItemRequest(variant_id=variant_id, branch_id=branch_id, quantity=payload.quantity)
        cart = await self._client.add_cart_item(state.cart.cart_id, req)
        state.cart.item_count = cart.total_quantity
        state.cart.subtotal = float(cart.subtotal)
        state.cart.items = [
            CartItemContext(
                item_id=str(i.item_id),
                product_name=i.product_name,
                color=i.color,
                size=i.size,
                quantity=i.quantity,
                price=float(i.unit_price)
            ) for i in cart.items
        ]
        return cart

    async def remove_cart_item(self, state: ConversationState, payload: RemoveCartItemPayload) -> CartView | None:
        if not state.cart.cart_id or not state.cart.items:
            return None
            
        target_item_id = None
        if payload.item_index is not None and 1 <= payload.item_index <= len(state.cart.items):
            target_item_id = state.cart.items[payload.item_index - 1].item_id
        elif payload.product_name:
            # Simple substring match
            for item in state.cart.items:
                if payload.product_name.lower() in item.product_name.lower():
                    target_item_id = item.item_id
                    break
                    
        if not target_item_id:
            return None
            
        from uuid import UUID
        cart = await self._client.remove_cart_item(state.cart.cart_id, UUID(target_item_id))
        state.cart.item_count = cart.total_quantity
        state.cart.subtotal = float(cart.subtotal)
        state.cart.items = [
            CartItemContext(
                item_id=str(i.item_id),
                product_name=i.product_name,
                color=i.color,
                size=i.size,
                quantity=i.quantity,
                price=float(i.unit_price)
            ) for i in cart.items
        ]
        return cart

    async def preview_checkout(self, state: ConversationState, offer_code: Optional[str] = None) -> StoreOrderPreview | None:
        if not state.cart.cart_id:
            return None
        req = PreviewCartRequest(offer_code=offer_code)
        return await self._client.preview_cart(state.cart.cart_id, req)

    async def place_order(
        self, 
        state: ConversationState, 
        payload: PlaceOrderPayload,
        offer_code: Optional[str] = None
    ) -> OrderView | None:
        if not state.cart.cart_id:
            return None
            
        req = PlaceOrderRequest(
            cart_id=state.cart.cart_id, 
            offer_code=offer_code,
            customer_name=payload.customer_name,
            phone=payload.phone,
            delivery_address=payload.delivery_address,
            city=payload.city,
            delivery_notes=payload.delivery_notes
        )
        order = await self._client.place_order(req)
        # Clear cart state after successful order
        state.cart.cart_id = None
        state.cart.item_count = 0
        state.cart.subtotal = 0.0
        state.cart.items = []
        return order

    async def get_promotions(self) -> str:
        """Fetch active promotions and format them as a string."""
        promos = await self._client.get_promotions()
        if not promos:
            return "No exclusive offers or promotions are currently running."
        
        lines = ["Currently active promotions:"]
        for p in promos:
            details = f"- {p.offer_name} (Code: {p.offer_code}): {p.description or 'Special offer'}"
            if p.discount_percentage:
                details += f" ({p.discount_percentage}% off)"
            elif p.discount_amount:
                details += f" (Rs {p.discount_amount} off)"
            lines.append(details)
        return "\n".join(lines)
