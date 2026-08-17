"""Agent-facing tool contracts for semantic interactions with the backend."""

import logging
from typing import Optional, Any

from app.agent.state import ConversationState, CartItemContext, ProductCard, CartCard, CheckoutCard, OrderCard
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
from uuid import UUID
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
    elif "active" in raw_lower:
        return "Activewear"
    elif "gym" in raw_lower:
        return "Gym Wear"
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


    async def search(
        self,
        state: ConversationState,
        payload: Optional[SearchProductsPayload] = None,
        limit_override: Optional[int] = None
    ) -> str:
        state.clear_cards()
        if payload is None:
            payload = SearchProductsPayload()
        
        if getattr(payload, "clear_previous_preferences", False):
            state.clear_search_preferences()
            
        categories_val = getattr(payload, "categories", None)
        query_val = getattr(payload, "search_query", None)
        category_name_val = getattr(payload, "category_name", None)
        if category_name_val and not categories_val:
            categories_val = [category_name_val]

        if categories_val is not None:
            parsed = parse_categories_from_input(categories_val, query_val)
            if parsed:
                state.categories = parsed
        elif not state.categories and query_val:
            parsed = parse_categories_from_input(None, query_val)
            if parsed:
                state.categories = parsed

        if getattr(payload, "product_types", None) is not None: state.product_types = payload.product_types
        if getattr(payload, "occasions", None) is not None: state.occasions = payload.occasions
        if getattr(payload, "colors", None) is not None: state.preferred_colors = payload.colors
        if getattr(payload, "excluded_colors", None) is not None: state.excluded_colors = payload.excluded_colors
        if getattr(payload, "materials", None) is not None: state.materials = payload.materials
        if getattr(payload, "fits", None) is not None: state.fits = payload.fits
        if getattr(payload, "seasons", None) is not None: state.seasons = payload.seasons
        if getattr(payload, "branch", None) is not None: state.branch_preference = payload.branch
        if getattr(payload, "sizes", None) is not None:
            for k, v in payload.sizes.items():
                state.size_preferences[k] = v
        if getattr(payload, "budget", None) is not None:
            if payload.budget.minimum is not None: state.budget.minimum = payload.budget.minimum
            if payload.budget.maximum is not None: state.budget.maximum = payload.budget.maximum
            
        budget_min = state.budget.minimum
        budget_max = state.budget.maximum
        
        if budget_max is None and state.displayed_products:
            min_displayed_price = min((p.price for p in state.displayed_products if p.price > 0), default=None)
            if min_displayed_price is not None:
                budget_max = float(min_displayed_price) - 0.01

        if limit_override is not None:
            limit = limit_override
        else:
            cats = state.categories or []
            limit = max(6, 3 * len(cats))
            limit = min(limit, 20)

        request = ProductSearchRequest(
            query_text=getattr(payload, "search_query", None),
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
            limit=min(limit, 20),
            article_code=getattr(payload, "specific_article", None),
        )

        logger.info(
            "agent_tool_get_products",
            extra={"event": "agent_tool_get_products", "filters": request.model_dump(exclude_defaults=True)},
        )

        response = await self._client.search_products(request)
        
        if state.categories and response.products:
            def _matches_category(p, requested_cats):
                cat_name = (p.category or "").lower().replace(" ", "").replace("-", "")
                prod_name = (p.product_name or "").lower().replace(" ", "").replace("-", "")
                prod_type = (p.product_type or "").lower().replace(" ", "").replace("-", "")
                for req in requested_cats:
                    req_stem = req.lower().replace(" ", "").replace("-", "").rstrip("s")
                    if req_stem == "shirt" and ("tshirt" in prod_type or "tshirt" in cat_name or "tee" in prod_type or "tee" in cat_name or "tee" in prod_name):
                        continue
                    if req_stem in cat_name or req_stem in prod_name or req_stem in prod_type:
                        return True
                    if cat_name in req_stem or prod_type in req_stem:
                        return True
                return False

            matched = [p for p in response.products if _matches_category(p, state.categories)]
            response.products = matched[:limit]
            response.result_count = len(response.products)
        else:
            response.products = response.products[:limit]
            response.result_count = len(response.products)

        state.record_displayed_products(response.products)
        state.product_cards = [ProductCard(product=p) for p in response.products]
        
        if not response.products:
            return "No products found matching the criteria."
        lines = [f"Found {len(response.products)} products:"]
        for idx, p in enumerate(response.products, 1):
            lines.append(f"Option {idx}: {p.product_name} | Price: Rs {p.final_price} | Type: {p.product_type} | Category: {p.category}")
        return "\n".join(lines)


    async def get_details(self, arg1: Any, arg2: Any = None) -> Any:
        if isinstance(arg1, ConversationState):
            state, payload = arg1, arg2
        else:
            payload, state = arg1, arg2

        if not state:
            return None

        product_id = getattr(payload, "product_id", None) if payload else None
        selected_index = getattr(payload, "selected_product_index", None) if payload else None

        target_product_ids = []
        if product_id:
            target_product_ids.append(product_id)
        elif selected_index is not None and state.displayed_products:
            if 1 <= selected_index <= len(state.displayed_products):
                target_product_ids.append(state.displayed_products[selected_index - 1].product_id)

        if not target_product_ids and state.displayed_products:
            target_product_ids = [dp.product_id for dp in state.displayed_products]

        if not target_product_ids:
            return None

        state.clear_cards()
        detailed_products = []
        lines = []

        for pid in target_product_ids:
            logger.info(
                "agent_tool_get_product_details",
                extra={"event": "agent_tool_get_product_details", "product_id": pid},
            )
            details = await self._client.get_product(pid)
            if details and details.product:
                p = details.product
                detailed_products.append(p)
                line_entry = [f"Details for {p.product_name}:", f"Price: Rs {p.final_price}", f"Description: {p.description or 'N/A'}"]
                if p.variants:
                    colors = sorted(list(set(v.color for v in p.variants if v.is_available)))
                    sizes = sorted(list(set(v.size for v in p.variants if v.is_available)))
                    line_entry.append(f"Available Colors: {', '.join(colors) if colors else 'None'}")
                    line_entry.append(f"Available Sizes: {', '.join(sizes) if sizes else 'None'}")
                lines.append("\n".join(line_entry))

        if detailed_products:
            state.record_displayed_products(detailed_products)
            state.product_cards = [ProductCard(product=p) for p in detailed_products]
            return "\n\n".join(lines)
        return None

    # Method aliases for backward compatibility and test expectations
    async def get_products(self, state: ConversationState, payload: Optional[SearchProductsPayload] = None, limit_override: Optional[int] = None) -> Any:
        return await self.search(state, payload, limit_override)

    async def explore_category(self, state: ConversationState, payload: Any = None) -> Any:
        return await self.search(state, payload)

    async def get_product_details(self, arg1: Any, arg2: Any = None) -> Any:
        return await self.get_details(arg1, arg2)

    async def add_cart_item(self, state: ConversationState, payload: AddCartItemPayload) -> Any:
        return await self.add_to_cart(state, payload)

    async def remove_cart_item(self, state: ConversationState, payload: RemoveCartItemPayload) -> Any:
        return await self.remove_cart(state, payload)

    async def preview_checkout(self, state: ConversationState, payload: Optional[PreviewCheckoutPayload] = None) -> Any:
        return await self.checkout(state, payload)


    async def _ensure_cart(self, state: ConversationState) -> None:
        """Create a cart for the session if it doesn't exist."""
        if not state.cart.cart_id:
            cart = await self._client.create_cart()
            state.cart.cart_id = cart.cart_id
            state.cart.item_count = cart.total_quantity
            state.cart.subtotal = float(cart.subtotal)
            state.cart.items = []


    async def add_to_cart(self, state: ConversationState, payload: AddCartItemPayload) -> str:
        state.clear_cards()
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
            return "Cannot determine which product to add."
            
        details = await self._client.get_product(product_id)
        if not details or not details.product or not details.product.variants:
            return "Product variants not available."

        in_stock_variants = [v for v in details.product.variants if v.is_available]
        if not in_stock_variants:
            in_stock_variants = details.product.variants

        if not payload.color or not payload.size:
            logger.info("add_cart_item_missing_color_or_size", extra={"color": payload.color, "size": payload.size, "product_id": product_id})
            colors = sorted(list(set(v.color for v in details.product.variants if v.is_available)))
            sizes = sorted(list(set(v.size for v in details.product.variants if v.is_available)))
            if state:
                state.record_displayed_products([details.product])
                state.product_cards = [ProductCard(product=details.product)]
            return (
                f"Cannot add {details.product.product_name} to cart directly because variant selection (color and size) is required.\n"
                f"Available Colors: {', '.join(colors) if colors else 'None'}\n"
                f"Available Sizes: {', '.join(sizes) if sizes else 'None'}\n"
                "INSTRUCTION: Politely and professionally ask the user which color and size they prefer from the available options before adding to cart."
            )

        matching_variants = self._get_matching_variants(details.product.variants, payload.color, payload.size)
            
        if not matching_variants:
            return f"Variant not found for color {payload.color} and size {payload.size}."
            
        variant = matching_variants[0]
        variant_id = variant.variant_id
        
        branch_id = None
        for a in variant.branch_availability:
            if a.is_available and a.available_quantity > 0:
                branch_id = a.branch_id
                break
                
        if not branch_id:
            return "Selected variant is currently out of stock."

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
        state.cart_card = CartCard(
            cart_id=str(cart.cart_id),
            items=cart.items,
            item_count=cart.total_quantity,
            subtotal=float(cart.subtotal)
        )
        return "Item successfully added to cart."

    def _get_matching_variants(self, variants, color: Optional[str], size: Optional[str]):
        matching = []
        for v in variants:
            if color and v.color.lower() != color.lower():
                continue
            if size and v.size.lower() != size.lower():
                continue
            matching.append(v)
        return matching

    def _resolve_cart_item_id(self, state: ConversationState, item_index: Optional[int], product_name: Optional[str]) -> Optional[str]:
        if not state.cart.items:
            return None
        if item_index is not None and 1 <= item_index <= len(state.cart.items):
            return state.cart.items[item_index - 1].item_id
        if product_name:
            for item in state.cart.items:
                if product_name.lower() in item.product_name.lower():
                    return item.item_id
        return None


    async def remove_cart(self, state: ConversationState, payload: RemoveCartItemPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id or not state.cart.items:
            return "Cart is already empty."
            
        target_item_id = self._resolve_cart_item_id(state, payload.item_index, payload.product_name)
                    
        if not target_item_id:
            return "Could not identify which item to remove."
            
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
        state.cart_card = CartCard(
            cart_id=str(cart.cart_id),
            items=cart.items,
            item_count=cart.total_quantity,
            subtotal=float(cart.subtotal)
        )
        return "Item successfully removed from cart."


    async def checkout(self, state: ConversationState, payload: PreviewCheckoutPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id:
            return "Cart is empty."
        req = PreviewCartRequest()
        preview = await self._client.preview_cart(state.cart.cart_id, req)
        
        applied_offers = []
        for o in preview.applied_offers:
            applied_offers.append(o.offer_name)
            
        state.checkout_card = CheckoutCard(
            subtotal=float(preview.subtotal),
            discount_total=float(preview.discount_total),
            delivery_fee=float(preview.delivery_fee),
            total_amount=float(preview.total_amount),
            applied_offers=applied_offers
        )
        
        lines = ["Checkout Preview:"]
        lines.append(f"Subtotal: Rs {preview.subtotal}")
        if preview.discount_total > 0:
            lines.append(f"Discount: Rs {preview.discount_total}")
        lines.append(f"Delivery: Rs {preview.delivery_fee}")
        lines.append(f"Total: Rs {preview.total_amount}")
        return "\n".join(lines)


    async def place_order(
        self, 
        state: ConversationState, 
        payload: PlaceOrderPayload
    ) -> str:
        state.clear_cards()
        if not state.cart.cart_id:
            return "Cart is empty."
            
        req = PlaceOrderRequest(
            cart_id=state.cart.cart_id, 
            offer_code=None,
            customer_name=payload.customer_name,
            phone=payload.phone,
            delivery_address=payload.delivery_address,
            city=payload.city,
            delivery_notes=payload.delivery_notes
        )
        order = await self._client.place_order(req)
        state.order_card = OrderCard(
            order_number=order.order_number,
            total_amount=float(order.total_amount),
            estimated_delivery_days="5-7"
        )
        # Clear cart state after successful order
        state.cart.cart_id = None
        state.cart.item_count = 0
        state.cart.subtotal = 0.0
        state.cart.items = []
        return f"Order placed successfully! Order Number: {order.order_number}. Total: Rs {order.total_amount}."


    async def show_cart(self, state: ConversationState, payload: ShowCartPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id:
            return "Cart is currently empty."
        cart = await self._client.get_cart(state.cart.cart_id)
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
        state.cart_card = CartCard(
            cart_id=str(cart.cart_id),
            items=cart.items,
            item_count=cart.total_quantity,
            subtotal=float(cart.subtotal)
        )
        return f"Cart has {cart.total_quantity} items. Subtotal: Rs {cart.subtotal}."

    async def update_cart_item(self, state: ConversationState, payload: UpdateCartItemPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id or not state.cart.items:
            return "Cart is empty."
        
        target_item_id = self._resolve_cart_item_id(state, payload.item_index, payload.product_name)
        if not target_item_id:
            return "Could not find that item in the cart."
            
        from app.clients.clothing_app.schemas import UpdateCartItemRequest
        req = UpdateCartItemRequest(quantity=payload.new_quantity)
        cart = await self._client.update_cart_item(state.cart.cart_id, UUID(target_item_id), req)
        
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
        state.cart_card = CartCard(
            cart_id=str(cart.cart_id),
            items=cart.items,
            item_count=cart.total_quantity,
            subtotal=float(cart.subtotal)
        )
        return f"Updated item quantity to {payload.new_quantity}."

    async def clear_cart(self, state: ConversationState, payload: ClearCartPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id:
            return "Cart is already empty."
        
        cart = await self._client.clear_cart(state.cart.cart_id)
        
        state.cart.item_count = cart.total_quantity
        state.cart.subtotal = float(cart.subtotal)
        state.cart.items = []
        state.cart_card = CartCard(
            cart_id=str(cart.cart_id),
            items=[],
            item_count=cart.total_quantity,
            subtotal=float(cart.subtotal)
        )
        return "Cart cleared."
        
    async def check_availability(self, state: ConversationState, payload: CheckAvailabilityPayload) -> str:
        state.clear_cards()
        details = await self._client.get_product(payload.product_id)
        if not details or not details.product or not details.product.variants:
            return "Product not found or has no variants."
            
        matching = self._get_matching_variants(details.product.variants, payload.color, payload.size)
            
        if not matching:
            return "No matching variants found for that color/size."
            
        variant_id = matching[0].variant_id
        
        branch_id = None
        if payload.branch:
            branches = await self._client.list_branches()
            for b in branches:
                if payload.branch.lower() in b.name.lower():
                    branch_id = b.branch_id
                    break
        
        if not branch_id and state.branch_preference:
            branches = await self._client.list_branches()
            for b in branches:
                if state.branch_preference.lower() in b.name.lower():
                    branch_id = b.branch_id
                    break
                    
        if not branch_id:
            branches = await self._client.list_branches()
            if branches:
                branch_id = branches[0].branch_id
                
        if not branch_id:
            return "Could not determine a store branch to check."
            
        avail = await self._client.get_availability(variant_id, branch_id)
        if avail and avail.is_available:
            return f"Yes, that's in stock. {avail.available_quantity} available."
        return "Sorry, that item is currently out of stock at this branch."
        
    async def get_order_status(self, state: ConversationState, payload: GetOrderStatusPayload) -> str:
        state.clear_cards()
        order = await self._client.get_order(payload.order_id)
        if not order:
            return "Order not found."
            
        state.order_card = OrderCard(
            order_number=order.order_number,
            total_amount=float(order.total_amount),
            estimated_delivery_days="5-7"
        )
        return f"Order {order.order_number} is {order.status}."

    async def get_promotions(self, state: ConversationState, payload: GetPromotionsPayload) -> str:
        """Fetch active promotions and format them as a string."""
        state.clear_cards()
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
