"""Cart business operations with catalog-backed stock and price validation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.cart.repository import CartRecord, CartRepository
from app.cart.schemas import AddCartItemRequest, CartItemView, CartView
from app.catalog.service import CatalogService
from app.config import AppConfig
from app.shared.errors import ConflictError


class CartService:
    """Manage temporary carts without trusting product data from the caller."""

    def __init__(
        self,
        repository: CartRepository,
        catalog: CatalogService,
        config: AppConfig,
    ) -> None:
        self._repository = repository
        self._catalog = catalog
        self._config = config

    async def create(self) -> CartView:
        """Create an empty temporary cart for the demo UI or clothing agent."""

        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self._config.cart_ttl_hours
        )
        return self._to_view(await self._repository.create(expires_at=expires_at))

    async def get(self, cart_id: UUID) -> CartView:
        """Return the current temporary cart."""

        return self._to_view(await self._repository.require(cart_id))

    async def add(self, cart_id: UUID, request: AddCartItemRequest) -> CartView:
        """Add an exact variant after validating current PostgreSQL stock and price."""

        cart = await self._repository.require(cart_id)
        snapshot = await self._catalog.variant_snapshot(
            request.variant_id,
            request.branch_id,
        )
        current_quantity = sum(
            item.quantity
            for item in cart.items.values()
            if item.variant_id == request.variant_id
            and item.branch_id == request.branch_id
        )
        requested_total = current_quantity + request.quantity
        if snapshot.available_quantity < requested_total:
            raise ConflictError(
                "The requested quantity is no longer available.",
                code="OUT_OF_STOCK",
            )
        updated = await self._repository.add_or_increment(
            cart_id,
            snapshot,
            request.quantity,
        )
        return self._to_view(updated)

    async def update(self, cart_id: UUID, item_id: UUID, quantity: int) -> CartView:
        """Replace one quantity after refreshing live stock and price."""

        item = await self._repository.item(cart_id, item_id)
        snapshot = await self._catalog.variant_snapshot(item.variant_id, item.branch_id)
        if snapshot.available_quantity < quantity:
            raise ConflictError(
                "The requested quantity is no longer available.",
                code="OUT_OF_STOCK",
            )
        updated = await self._repository.update_quantity(
            cart_id,
            item_id,
            quantity,
            unit_price=snapshot.unit_price,
        )
        return self._to_view(updated)

    async def remove(self, cart_id: UUID, item_id: UUID) -> CartView:
        """Remove one item from the cart."""

        return self._to_view(await self._repository.remove_item(cart_id, item_id))

    async def clear(self, cart_id: UUID) -> CartView:
        """Clear all items while retaining the cart ID."""

        return self._to_view(await self._repository.clear(cart_id))

    @staticmethod
    def _to_view(cart: CartRecord) -> CartView:
        """Convert internal records into the stable API response contract."""

        items: list[CartItemView] = []
        subtotal = Decimal("0.00")
        total_quantity = 0
        for item in cart.items.values():
            line_total = item.unit_price * item.quantity
            subtotal += line_total
            total_quantity += item.quantity
            items.append(
                CartItemView(
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
                    line_total=line_total,
                    image_url=item.image_url,
                )
            )
        return CartView(
            cart_id=cart.cart_id,
            items=items,
            total_quantity=total_quantity,
            subtotal=subtotal,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
            expires_at=cart.expires_at,
        )
