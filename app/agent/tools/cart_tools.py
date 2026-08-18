"""Cart tool handlers for adding, removing, updating, showing, and clearing cart items."""

import logging
from typing import Optional, Any
from uuid import UUID

from app.agent.state import ConversationState, CartItemContext, ProductCard, CartCard
from app.agent.schemas import (
    AddCartItemPayload,
    RemoveCartItemPayload,
    ShowCartPayload,
    UpdateCartItemPayload,
    ClearCartPayload
)
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import AddCartItemRequest, UpdateCartItemRequest

logger = logging.getLogger(__name__)


from app.agent.tools.helpers import normalize_size_label, normalize_color_name, is_color_match, is_size_match


class CartToolsMixin:
    """Cart management capabilities."""

    _client: ClothingAppClient

    async def _ensure_cart(self, state: ConversationState) -> None:
        """Create a cart for the session if it doesn't exist."""
        if not state.cart.cart_id:
            cart = await self._client.create_cart()
            state.cart.cart_id = cart.cart_id
            state.cart.item_count = cart.total_quantity
            state.cart.subtotal = float(cart.subtotal)
            state.cart.items = []

    def _get_matching_variants(self, variants: list[Any], color: Optional[str], size: Optional[str]) -> list[Any]:
        matching = []
        for v in variants:
            if color and not is_color_match(color, v.color):
                continue
            if size and not is_size_match(size, v.size):
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

        req_color = payload.color
        req_size = payload.size

        if not req_color and state.preferred_colors:
            req_color = state.preferred_colors[0]

        if not req_size and state.size_preferences:
            req_size = list(state.size_preferences.values())[0]

        if not req_color or not req_size:
            logger.info("add_cart_item_missing_color_or_size", extra={"color": req_color, "size": req_size, "product_id": product_id})
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

        matching_variants = self._get_matching_variants(details.product.variants, req_color, req_size)
            
        if not matching_variants:
            return f"Variant not found for color {req_color} and size {req_size}."
            
        variant = matching_variants[0]
        variant_id = variant.variant_id
        
        branch_id = None
        for a in variant.branch_availability:
            if a.branch_id:
                branch_id = a.branch_id
                if a.is_available and (a.available_quantity or 0) > 0:
                    break
                
        if not branch_id:
            branch_id = 1

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
        if details and details.product:
            state.record_displayed_products([details.product])
            state.product_cards = [ProductCard(product=details.product)]
        cart_item_lines = [
            f"{idx}. {item.product_name} – Color: {item.color}, Size: {item.size}, Quantity: {item.quantity}, Price: {int(float(item.unit_price))} rupees."
            for idx, item in enumerate(cart.items, 1)
        ]
        return (
            f"Successfully added {payload.quantity}x {details.product.product_name} ({payload.color}, {payload.size}) to cart.\n\n"
            f"Updated Cart Contents ({cart.total_quantity} items total, Subtotal: {int(float(cart.subtotal))} rupees):\n"
            + "\n".join(cart_item_lines)
        )

    async def add_cart_item(self, state: ConversationState, payload: AddCartItemPayload) -> Any:
        return await self.add_to_cart(state, payload)

    async def remove_cart(self, state: ConversationState, payload: RemoveCartItemPayload) -> str:
        state.clear_cards()
        await self._ensure_cart(state)
        
        target_item_id = payload.cart_item_id
        if not target_item_id:
            target_item_id = self._resolve_cart_item_id(state, payload.item_index, payload.product_name)
            
        if not target_item_id and state.cart.items:
            target_item_id = state.cart.items[0].item_id
            
        if not target_item_id:
            return "No items found in cart to remove."

        target_item = next((i for i in state.cart.items if i.item_id == target_item_id), None)
        removed_product = None

        if target_item:
            try:
                search_res = await self._client.search_products(ProductSearchRequest(query_text=target_item.product_name, limit=1))
                if search_res and search_res.products:
                    removed_product = search_res.products[0]
            except Exception as e:
                logger.warning(f"Could not fetch product details for removed item: {e}")
        elif state.cart_card and state.cart_card.items:
            pid = None
            for ci in state.cart_card.items:
                if str(ci.item_id) == target_item_id:
                    pid = ci.product_id
                    break
            if pid:
                try:
                    details = await self._client.get_product(pid)
                    if details and details.product:
                        removed_product = details.product
                except Exception as e:
                    logger.warning(f"Could not fetch product details for removed item: {e}")

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

        if removed_product:
            state.record_displayed_products([removed_product])
            state.product_cards = [ProductCard(product=removed_product)]
        elif cart.items:
            remaining_products = []
            seen_pids = set()
            for ci in cart.items:
                if ci.product_id not in seen_pids:
                    seen_pids.add(ci.product_id)
                    try:
                        details = await self._client.get_product(ci.product_id)
                        if details and details.product:
                            remaining_products.append(details.product)
                    except Exception:
                        pass
            if remaining_products:
                state.record_displayed_products(remaining_products)
                state.product_cards = [ProductCard(product=p) for p in remaining_products]

        if not cart.items:
            return f"Successfully removed {target_item.product_name if target_item else 'item'} from cart. Cart is now empty."

        item_lines = [
            f"{idx}. {item.product_name} – Color: {item.color}, Size: {item.size}, Quantity: {item.quantity}, Price: {int(float(item.unit_price))} rupees."
            for idx, item in enumerate(cart.items, 1)
        ]
        return (
            f"Successfully removed {target_item.product_name if target_item else 'item'} from cart.\n\n"
            f"Remaining Cart Contents ({cart.total_quantity} items total, Subtotal: {int(float(cart.subtotal))} rupees):\n"
            + "\n".join(item_lines)
        )

    async def remove_cart_item(self, state: ConversationState, payload: RemoveCartItemPayload) -> Any:
        return await self.remove_cart(state, payload)

    async def show_cart(self, state: ConversationState, payload: ShowCartPayload) -> str:
        state.clear_cards()
        await self._ensure_cart(state)
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
        if not cart.items:
            return "Cart is currently empty."

        cart_products = []
        seen_pids = set()
        for item in cart.items:
            if item.product_id not in seen_pids:
                seen_pids.add(item.product_id)
                try:
                    details = await self._client.get_product(item.product_id)
                    if details and details.product:
                        cart_products.append(details.product)
                except Exception as e:
                    logger.warning(f"Failed to fetch cart product details {item.product_id}: {e}")

        if cart_products:
            state.record_displayed_products(cart_products)
            state.product_cards = [ProductCard(product=p) for p in cart_products]

        item_lines = [
            f"{idx}. {item.product_name} – Color: {item.color}, Size: {item.size}, Quantity: {item.quantity}, Price: {int(float(item.unit_price))} rupees."
            for idx, item in enumerate(cart.items, 1)
        ]
        return f"Current Cart Contents ({cart.total_quantity} items total, Subtotal: {int(float(cart.subtotal))} rupees):\n" + "\n".join(item_lines)

    async def update_cart_item(self, state: ConversationState, payload: UpdateCartItemPayload) -> str:
        state.clear_cards()
        if not state.cart.cart_id or not state.cart.items:
            return "Cart is empty."
        
        target_item_id = self._resolve_cart_item_id(state, payload.item_index, payload.product_name)
        if not target_item_id:
            return "Could not find that item in the cart."
            
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
