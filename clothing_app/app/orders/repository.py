"""Transactional repository for order creation and retrieval."""
from __future__ import annotations

import uuid
import secrets
import string
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.orders.models import Order, OrderItem
from app.cart.models import Cart
from app.common.exceptions import ConflictError, NotFoundError
from app.config import get_config
from app.inventory.reservations import ReservationService


class OrderRepository:
    """Own the order persistence boundary inside the caller's transaction."""

    def __init__(self, db: AsyncSession, reservations: ReservationService) -> None:
        self._db = db
        self._reservations = reservations

    @staticmethod
    def _generate_order_number() -> str:
        """Generate a customer-safe unique order number candidate."""
        return "ORD-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    async def get_by_checkout_request_id(self, checkout_request_id: str) -> Order | None:
        """Return an existing order for an idempotent placement request."""
        result = await self._db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.checkout_request_id == checkout_request_id, Order.store_id == get_config().store_id)
        )
        return result.scalars().first()

    async def create_order_from_cart(self, cart: Cart, preview, request) -> Order:
        """Create order and deduct inventory atomically within the current transaction.

        Inventory rows are locked before availability is recalculated. If any item is
        short, the exception aborts the surrounding transaction and no order is stored.
        """
        existing = await self.get_by_checkout_request_id(request.checkout_request_id)
        if existing:
            return existing

        order_id = uuid.uuid4()
        # ReservationService holds and converts inventory atomically under row locks.
        consumed = await self._reservations.consume_for_order(cart.cart_id)
        for item in cart.items:
            key = (item.variant_id, item.branch_id)
            if key in consumed:
                continue
            # Legacy carts created before reservations were introduced are revalidated
            # and deducted under a row lock exactly once.
            from app.inventory.models import BranchInventory
            result = await self._db.execute(
                select(BranchInventory).where(
                    BranchInventory.variant_id == item.variant_id,
                    BranchInventory.branch_id == item.branch_id,
                ).with_for_update()
            )
            inventory = result.scalars().first()
            if not inventory:
                raise ConflictError("Inventory record no longer exists.", code="INVENTORY_NOT_FOUND")
            available = inventory.quantity_on_hand - inventory.reserved_quantity - inventory.damaged_quantity
            if available < item.quantity:
                raise ConflictError(f"Insufficient stock for variant {item.variant_id}.", code="OUT_OF_STOCK")
            inventory.quantity_on_hand -= item.quantity

        order = Order(
            order_id=order_id,
            order_number=self._generate_order_number(),
            checkout_request_id=request.checkout_request_id,
            session_id=cart.session_id,
            store_id=cart.store_id,
            subtotal=preview.subtotal,
            discount_total=preview.discount_total,
            delivery_fee=preview.delivery_fee,
            grand_total=preview.grand_total,
            applied_offer_code=preview.applied_offer_code,
            status="PLACED",
            customer_name=request.customer_name,
            phone=request.phone,
            delivery_address=request.delivery_address,
            city=request.city,
            delivery_notes=request.delivery_notes,
        )
        self._db.add(order)

        for item in preview.items:
            self._db.add(OrderItem(
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
            ))

        await self._db.flush()
        result = await self._db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id, Order.store_id == get_config().store_id)
        )
        return result.scalars().first()

    async def get_order(self, order_id: uuid.UUID) -> Order:
        """Return one order with immutable item snapshots."""
        result = await self._db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id, Order.store_id == get_config().store_id)
        )
        order = result.scalars().first()
        if not order:
            raise NotFoundError("Order not found.", code="ORDER_NOT_FOUND")
        return order
