"""PostgreSQL repository for persistent carts and cart items."""
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.cart.models import Cart, CartItem
from app.common.exceptions import NotFoundError
from app.config import get_config


class CartRepository:
    """Persist cart state while keeping transaction ownership at the API request boundary."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, session_id: str, store_id: str, expires_at: datetime) -> Cart:
        """Create a cart for a session."""
        cart = Cart(cart_id=uuid4(), session_id=session_id, store_id=store_id, expires_at=expires_at)
        self._db.add(cart)
        await self._db.flush()
        return await self.require(cart.cart_id)

    async def get_by_session(self, session_id: str, store_id: str) -> Cart | None:
        """Return the active cart for a session and store."""
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(Cart).options(selectinload(Cart.items)).where(
                Cart.session_id == session_id,
                Cart.store_id == store_id,
                Cart.expires_at > now,
            )
        )
        return result.scalars().first()

    async def require(self, cart_id: UUID, *, for_update: bool = False) -> Cart:
        """Load a non-expired cart, optionally locking it for mutation."""
        now = datetime.now(timezone.utc)
        statement = select(Cart).options(selectinload(Cart.items)).where(
            Cart.cart_id == cart_id,
            Cart.expires_at > now,
        )
        if for_update:
            statement = statement.with_for_update()
        result = await self._db.execute(statement)
        cart = result.scalars().first()
        if not cart:
            raise NotFoundError("Cart was not found or has expired.", code="CART_NOT_FOUND")
        return cart

    async def add_or_increment(self, cart_id: UUID, product_id: int, variant_id: int, branch_id: int, quantity: int) -> Cart:
        """Atomically mutate one cart while holding the cart row lock."""
        cart = await self.require(cart_id, for_update=True)
        existing = next((i for i in cart.items if i.variant_id == variant_id and i.branch_id == branch_id), None)
        if existing:
            existing.quantity += quantity
        else:
            item = CartItem(
                item_id=uuid4(), cart_id=cart.cart_id, product_id=product_id,
                variant_id=variant_id, branch_id=branch_id, quantity=quantity,
            )
            self._db.add(item)
            cart.items.append(item)
        cart.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return cart

    async def update_quantity(self, cart_id: UUID, item_id: UUID, quantity: int) -> Cart:
        """Replace an item quantity while holding the cart row lock."""
        cart = await self.require(cart_id, for_update=True)
        item = next((i for i in cart.items if i.item_id == item_id), None)
        if not item:
            raise NotFoundError("Cart item not found.", code="CART_ITEM_NOT_FOUND")
        item.quantity = quantity
        cart.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return cart

    async def remove_item(self, cart_id: UUID, item_id: UUID) -> Cart:
        """Remove one item while holding the cart row lock."""
        cart = await self.require(cart_id, for_update=True)
        item = next((i for i in cart.items if i.item_id == item_id), None)
        if not item:
            raise NotFoundError("Cart item not found.", code="CART_ITEM_NOT_FOUND")
        await self._db.delete(item)
        cart.items.remove(item)
        cart.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return cart

    async def clear(self, cart_id: UUID) -> Cart:
        """Remove all items while retaining the cart identity."""
        cart = await self.require(cart_id, for_update=True)
        for item in list(cart.items):
            await self._db.delete(item)
        cart.items.clear()
        cart.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return cart
