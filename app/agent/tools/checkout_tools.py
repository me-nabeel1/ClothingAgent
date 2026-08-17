"""Checkout tool handlers for order preview, placing orders, and tracking status."""

import logging
from typing import Optional, Any
from uuid import UUID

from app.agent.state import ConversationState, CheckoutCard, OrderCard
from app.agent.schemas import PreviewCheckoutPayload, PlaceOrderPayload, GetOrderStatusPayload
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import PreviewCartRequest, PlaceOrderRequest

logger = logging.getLogger(__name__)


class CheckoutToolsMixin:
    """Checkout and order management capabilities."""

    _client: ClothingAppClient

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
        lines.append(f"Subtotal: {int(float(preview.subtotal))} rupees.")
        if preview.discount_total > 0:
            lines.append(f"Discount: {int(float(preview.discount_total))} rupees.")
        lines.append(f"Delivery: {int(float(preview.delivery_fee))} rupees.")
        lines.append(f"Total: {int(float(preview.total_amount))} rupees.")
        return "\n".join(lines)

    async def preview_checkout(self, state: ConversationState, payload: Optional[PreviewCheckoutPayload] = None) -> Any:
        return await self.checkout(state, payload or PreviewCheckoutPayload())

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
        return f"Order placed successfully! Order Number: {order.order_number}. Total: {int(float(order.total_amount))} rupees."

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
