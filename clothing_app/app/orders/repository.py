"""SQLAlchemy repository for orders."""
import uuid
import random
import string
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.models import Order, OrderItem
from app.cart.models import Cart
from app.common.exceptions import NotFoundError
from app.inventory.models import BranchInventory

class OrderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _generate_order_number(self) -> str:
        """Generate a random alphanumeric 8-character order number."""
        return "ORD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    async def create_order_from_cart(self, cart: Cart, preview, items, request=None) -> Order:
        """Create a new order from a cart and preview data."""
        order_id = uuid.uuid4()
        
        for item in cart.items:
            result = await self._db.execute(
                select(BranchInventory).where(
                    BranchInventory.variant_id == item.variant_id,
                    BranchInventory.branch_id == item.branch_id
                ).with_for_update()
            )
            inv = result.scalars().first()
            if inv:
                inv.quantity_on_hand -= item.quantity
                
        order = Order(
            order_id=order_id,
            order_number=self._generate_order_number(),
            session_id=cart.session_id,
            store_id=cart.store_id,
            subtotal=preview.subtotal,
            discount_total=preview.discount_total,
            delivery_fee=preview.delivery_fee,
            grand_total=preview.grand_total,
            applied_offer_code=preview.applied_offer_code,
            status="PLACED",
            customer_name=request.customer_name if request else None,
            phone=request.phone if request else None,
            delivery_address=request.delivery_address if request else None,
            city=request.city if request else None,
            delivery_notes=request.delivery_notes if request else None
        )
        
        self._db.add(order)
        
        for item in items:
            order_item = OrderItem(
                item_id=uuid.uuid4(),
                order_id=order.order_id,
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
            )
            self._db.add(order_item)
            
        await self._db.flush()
        
        result = await self._db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id)
        )
        return result.scalars().first()

    async def get_order(self, order_id: uuid.UUID) -> Order:
        result = await self._db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id)
        )
        order = result.scalars().first()
        if not order:
            raise NotFoundError("Order not found.", code="ORDER_NOT_FOUND")
        return order
