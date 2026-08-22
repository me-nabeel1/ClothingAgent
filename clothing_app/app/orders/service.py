"""Order orchestration with checkout revalidation and idempotency."""
from __future__ import annotations
from uuid import UUID
from app.orders.repository import OrderRepository
from app.orders.schemas import OrderView, PlaceOrderRequest
from app.cart.repository import CartRepository
from app.cart.service import CartService
from app.cart.schemas import PreviewCartRequest, CartItemView
from app.common.exceptions import ConflictError


class OrderService:
    """Coordinate a single atomic cart-to-order transaction."""

    def __init__(self, repository: OrderRepository, cart_repo: CartRepository, cart_service: CartService) -> None:
        self._repository = repository
        self._cart_repo = cart_repo
        self._cart_service = cart_service

    async def place_order(self, request: PlaceOrderRequest) -> OrderView:
        """Re-evaluate checkout, lock inventory, create order, and clear cart atomically."""
        existing = await self._repository.get_by_checkout_request_id(request.checkout_request_id)
        if existing:
            return self._to_view(existing)

        cart = await self._cart_repo.require(request.cart_id, for_update=True)
        if not cart.items:
            raise ConflictError("Cannot place an order with an empty cart.", code="CART_EMPTY")
        if not cart.confirmation_token:
            raise ConflictError("Pending order confirmation is invalid or expired due to cart mutation. A new checkout preview is required.", code="CONFIRMATION_INVALID")

        preview = await self._cart_service.preview(request.cart_id, PreviewCartRequest(offer_code=request.offer_code))
        order = await self._repository.create_order_from_cart(cart, preview, request)
        await self._cart_repo.clear(request.cart_id)
        return self._to_view(order, items=preview.items)

    async def get_order(self, order_id: UUID) -> OrderView:
        """Return an immutable order snapshot."""
        order = await self._repository.get_order(order_id)
        items = [CartItemView(
            item_id=item.item_id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            branch_id=item.branch_id,
            article_code=item.article_code,
            product_name=item.product_name,
            color=item.color,
            size=item.size,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
            image_url=None,
        ) for item in order.items]
        return self._to_view(order, items=items)

    @staticmethod
    def _to_view(order, items=None) -> OrderView:
        """Map an ORM order into its API snapshot."""
        return OrderView(
            order_id=order.order_id,
            order_number=order.order_number,
            status=order.status,
            subtotal=order.subtotal,
            discount_total=order.discount_total,
            delivery_fee=order.delivery_fee,
            grand_total=order.grand_total,
            applied_offer_code=order.applied_offer_code,
            customer_name=order.customer_name,
            phone=order.phone,
            delivery_address=order.delivery_address,
            city=order.city,
            delivery_notes=order.delivery_notes,
            items=items or [],
            created_at=order.created_at,
        )
