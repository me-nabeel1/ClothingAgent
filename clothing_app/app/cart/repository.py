"""Process-local repository for temporary demo carts.

The clothing catalog remains in PostgreSQL. Carts are intentionally temporary
for this first demo stage, so this repository avoids depending on legacy session
or order tables. It can later be replaced without changing the cart service or
API contracts.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache
from uuid import UUID, uuid4

from app.catalog.schemas import VariantSnapshot
from app.shared.errors import NotFoundError


@dataclass(slots=True)
class CartItemRecord:
    """Internal mutable cart-item record."""

    item_id: UUID
    product_id: int
    variant_id: int
    branch_id: int
    article_code: str
    product_name: str
    color: str
    size: str
    quantity: int
    unit_price: Decimal
    image_url: str | None


@dataclass(slots=True)
class CartRecord:
    """Internal mutable cart record."""

    cart_id: UUID
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    items: dict[UUID, CartItemRecord] = field(default_factory=dict)


class CartRepository:
    """Concurrency-safe repository for short-lived demonstration carts."""

    def __init__(self) -> None:
        self._carts: dict[UUID, CartRecord] = {}
        self._lock = asyncio.Lock()

    async def create(self, *, expires_at: datetime) -> CartRecord:
        """Create and store an empty temporary cart."""

        now = datetime.now(timezone.utc)
        cart = CartRecord(
            cart_id=uuid4(),
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )
        async with self._lock:
            self._carts[cart.cart_id] = cart
        return cart

    async def require(self, cart_id: UUID) -> CartRecord:
        """Return a non-expired cart or raise a stable not-found error."""

        async with self._lock:
            cart = self._carts.get(cart_id)
            if cart and cart.expires_at <= datetime.now(timezone.utc):
                self._carts.pop(cart_id, None)
                cart = None
            if not cart:
                raise NotFoundError("Cart was not found or has expired.", code="CART_NOT_FOUND")
            return cart

    async def add_or_increment(
        self,
        cart_id: UUID,
        snapshot: VariantSnapshot,
        quantity: int,
    ) -> CartRecord:
        """Add a new variant or increment its matching branch-specific item."""

        async with self._lock:
            cart = self._require_unlocked(cart_id)
            existing = next(
                (
                    item
                    for item in cart.items.values()
                    if item.variant_id == snapshot.variant_id
                    and item.branch_id == snapshot.branch_id
                ),
                None,
            )
            if existing:
                existing.quantity += quantity
                existing.unit_price = snapshot.unit_price
            else:
                item = CartItemRecord(
                    item_id=uuid4(),
                    product_id=snapshot.product_id,
                    variant_id=snapshot.variant_id,
                    branch_id=snapshot.branch_id,
                    article_code=snapshot.article_code,
                    product_name=snapshot.product_name,
                    color=snapshot.color,
                    size=snapshot.size,
                    quantity=quantity,
                    unit_price=snapshot.unit_price,
                    image_url=snapshot.image_url,
                )
                cart.items[item.item_id] = item
            cart.updated_at = datetime.now(timezone.utc)
            return cart

    async def update_quantity(
        self,
        cart_id: UUID,
        item_id: UUID,
        quantity: int,
        *,
        unit_price: Decimal,
    ) -> CartRecord:
        """Replace an item quantity and refresh its trusted price."""

        async with self._lock:
            cart = self._require_unlocked(cart_id)
            item = cart.items.get(item_id)
            if not item:
                raise NotFoundError("Cart item was not found.", code="CART_ITEM_NOT_FOUND")
            item.quantity = quantity
            item.unit_price = unit_price
            cart.updated_at = datetime.now(timezone.utc)
            return cart

    async def remove_item(self, cart_id: UUID, item_id: UUID) -> CartRecord:
        """Remove one item while retaining the cart identity."""

        async with self._lock:
            cart = self._require_unlocked(cart_id)
            if item_id not in cart.items:
                raise NotFoundError("Cart item was not found.", code="CART_ITEM_NOT_FOUND")
            cart.items.pop(item_id)
            cart.updated_at = datetime.now(timezone.utc)
            return cart

    async def clear(self, cart_id: UUID) -> CartRecord:
        """Remove all items from a cart."""

        async with self._lock:
            cart = self._require_unlocked(cart_id)
            cart.items.clear()
            cart.updated_at = datetime.now(timezone.utc)
            return cart

    async def item(self, cart_id: UUID, item_id: UUID) -> CartItemRecord:
        """Return one item for service-level stock validation."""

        async with self._lock:
            cart = self._require_unlocked(cart_id)
            item = cart.items.get(item_id)
            if not item:
                raise NotFoundError("Cart item was not found.", code="CART_ITEM_NOT_FOUND")
            return item

    def _require_unlocked(self, cart_id: UUID) -> CartRecord:
        """Return a cart while the repository lock is already held."""

        cart = self._carts.get(cart_id)
        if cart and cart.expires_at <= datetime.now(timezone.utc):
            self._carts.pop(cart_id, None)
            cart = None
        if not cart:
            raise NotFoundError("Cart was not found or has expired.", code="CART_NOT_FOUND")
        return cart


@lru_cache
def get_cart_repository() -> CartRepository:
    """Return the process-wide temporary-cart repository."""

    return CartRepository()
