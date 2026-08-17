"""Order business logic."""
from uuid import UUID
from app.orders.repository import OrderRepository
from app.orders.schemas import OrderView, PlaceOrderRequest
from app.cart.repository import CartRepository
from app.cart.service import CartService
from app.cart.schemas import PreviewCartRequest
from app.common.exceptions import ConflictError

class OrderService:
    def __init__(self, repository: OrderRepository, cart_repo: CartRepository, cart_service: CartService) -> None:
        self._repository = repository
        self._cart_repo = cart_repo
        self._cart_service = cart_service

    async def place_order(self, request: PlaceOrderRequest) -> OrderView:
        cart = await self._cart_repo.require(request.cart_id)
        if not cart.items:
            raise ConflictError("Cannot place an order with an empty cart.", code="CART_EMPTY")
            
        preview = await self._cart_service.preview(
            request.cart_id, 
            PreviewCartRequest(offer_code=request.offer_code)
        )
        
        order = await self._repository.create_order_from_cart(cart, preview, preview.items, request)
        
        await self._cart_repo.clear(request.cart_id)
        
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
            items=preview.items,
            created_at=order.created_at
        )

    async def get_order(self, order_id: UUID) -> OrderView:
        order = await self._repository.get_order(order_id)
        
        from app.cart.schemas import CartItemView
        items = []
        for item in order.items:
            items.append(CartItemView(
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
                image_url=None
            ))
            
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
            items=items,
            created_at=order.created_at
        )
