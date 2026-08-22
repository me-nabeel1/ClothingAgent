"""Cart business operations with persistent storage and authoritative pricing."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.cart.repository import CartRepository
from app.cart.models import Cart
from app.cart.schemas import (
    AddCartItemRequest, CartItemView, CartView, StoreOrderPreview, PreviewCartRequest,
)
from app.inventory.service import InventoryService
from app.inventory.reservations import ReservationService
from app.promotions.service import PromotionService
from app.config import AppConfig
from app.common.exceptions import ConflictError
from app.common.media import resolve_product_image_url


class CartService:
    """Coordinate cart persistence, inventory validation, and checkout evaluation."""

    def __init__(self, repository: CartRepository, inventory: InventoryService, promotions: PromotionService, config: AppConfig, reservations: ReservationService) -> None:
        self._repository = repository
        self._inventory = inventory
        self._promotions = promotions
        self._config = config
        self._reservations = reservations

    async def create(self, session_id: str | None = None, store_id: str | None = None) -> CartView:
        """Reuse an active session cart or create a new persistent cart."""
        session_id = session_id or f"anonymous-{uuid4().hex}"
        store_id = store_id or self._config.store_id
        await self._reservations.release_expired()
        existing = await self._repository.get_by_session(session_id, store_id)
        if existing:
            return await self._to_view(existing)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self._config.cart_ttl_hours)
        cart = await self._repository.create(session_id, store_id, expires_at)
        return await self._to_view(cart)

    async def get(self, cart_id: UUID) -> CartView:
        return await self._to_view(await self._repository.require(cart_id))

    async def add(self, cart_id: UUID, request: AddCartItemRequest) -> CartView:
        cart = await self._repository.require(cart_id, for_update=True)
        cart.confirmation_token = None
        snapshot = await self._inventory.variant_snapshot(request.variant_id, request.branch_id)
        current_quantity = sum(
            item.quantity for item in cart.items
            if item.variant_id == request.variant_id and item.branch_id == request.branch_id
        )
        total_quantity = current_quantity + request.quantity
        await self._reservations.reserve(
            cart_id, request.variant_id, request.branch_id, total_quantity, cart.expires_at
        )
        updated = await self._repository.add_or_increment(
            cart_id, snapshot.product_id, request.variant_id, request.branch_id, request.quantity
        )
        return await self._to_view(updated)

    async def update(self, cart_id: UUID, item_id: UUID, quantity: int) -> CartView:
        cart = await self._repository.require(cart_id, for_update=True)
        cart.confirmation_token = None
        item = next((i for i in cart.items if i.item_id == item_id), None)
        if not item:
            raise ConflictError("Item not found.", code="CART_ITEM_NOT_FOUND")
        if quantity > 0:
            await self._reservations.reserve(
                cart_id, item.variant_id, item.branch_id, quantity, cart.expires_at
            )
        else:
            await self._reservations.release_for_item(cart_id, item.variant_id, item.branch_id)
        return await self._to_view(await self._repository.update_quantity(cart_id, item_id, quantity))

    async def remove(self, cart_id: UUID, item_id: UUID) -> CartView:
        cart = await self._repository.require(cart_id, for_update=True)
        cart.confirmation_token = None
        item = next((i for i in cart.items if i.item_id == item_id), None)
        if not item:
            raise ConflictError("Cart item not found.", code="CART_ITEM_NOT_FOUND")
        await self._reservations.release_for_item(cart_id, item.variant_id, item.branch_id)
        return await self._to_view(await self._repository.remove_item(cart_id, item_id))

    async def clear(self, cart_id: UUID) -> CartView:
        cart = await self._repository.require(cart_id, for_update=True)
        cart.confirmation_token = None
        await self._reservations.release_for_cart(cart_id)
        return await self._to_view(await self._repository.clear(cart_id))

    async def preview(self, cart_id: UUID, request: PreviewCartRequest) -> StoreOrderPreview:
        """Re-read the cart and calculate authoritative offers and delivery, creating a new confirmation token."""
        await self._reservations.release_expired()
        cart = await self._repository.require(cart_id, for_update=True)
        confirmation_token = uuid4()
        cart.confirmation_token = confirmation_token
        view = await self._to_view(cart)
        evaluation = await self._promotions.evaluate_cart(view.subtotal, view.items, request.offer_code)
        delivery_fee = Decimal("0.00") if evaluation.free_delivery else self._delivery_fee(view.subtotal)
        grand_total = (view.subtotal - evaluation.discount_total + delivery_fee).quantize(Decimal("0.01"))
        codes = [offer.offer_code for offer in evaluation.applied_offers]
        return StoreOrderPreview(
            cart_id=view.cart_id,
            items=view.items,
            total_quantity=view.total_quantity,
            subtotal=view.subtotal,
            discount_total=evaluation.discount_total,
            delivery_fee=delivery_fee,
            grand_total=grand_total,
            applied_offer_code=codes[0] if codes else None,
            applied_offer_codes=codes,
            free_delivery=evaluation.free_delivery,
            confirmation_token=confirmation_token,
        )

    @staticmethod
    def _delivery_fee(subtotal: Decimal) -> Decimal:
        """Return the prototype delivery charge policy."""
        return Decimal("15.00") if subtotal > 0 and subtotal < Decimal("100.00") else Decimal("0.00")

    async def _to_view(self, cart: Cart) -> CartView:
        items: list[CartItemView] = []
        subtotal = Decimal("0.00")
        total_quantity = 0
        for item in cart.items:
            snapshot = await self._inventory.variant_snapshot(item.variant_id, item.branch_id)
            line_total = snapshot.unit_price * item.quantity
            subtotal += line_total
            total_quantity += item.quantity
            items.append(CartItemView(
                item_id=item.item_id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                branch_id=item.branch_id,
                article_code=snapshot.article_code,
                product_name=snapshot.product_name,
                category_id=snapshot.category_id,
                color=snapshot.color,
                size=snapshot.size,
                quantity=item.quantity,
                unit_price=snapshot.unit_price,
                line_total=line_total,
                image_url=resolve_product_image_url(snapshot.image_url, self._config.product_images_dir),
            ))
        return CartView(
            cart_id=cart.cart_id,
            session_id=cart.session_id,
            store_id=cart.store_id,
            items=items,
            total_quantity=total_quantity,
            subtotal=subtotal,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
            expires_at=cart.expires_at,
        )
