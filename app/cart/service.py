"""Cart business operations with persistent storage and promotion validation."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.cart.repository import CartRepository
from app.cart.models import Cart
from app.cart.schemas import (
    AddCartItemRequest,
    CartItemView,
    CartView,
    StoreOrderPreview,
    PreviewCartRequest,
)
from app.inventory.service import InventoryService
from app.promotions.service import PromotionService
from app.config import AppConfig
from app.common.exceptions import ConflictError


class CartService:
    def __init__(
        self,
        repository: CartRepository,
        inventory: InventoryService,
        promotions: PromotionService,
        config: AppConfig,
    ) -> None:
        self._repository = repository
        self._inventory = inventory
        self._promotions = promotions
        self._config = config

    def _resolve_image_url(self, image_url: str | None) -> str | None:
        if not image_url:
            return None
        return f"/assets/products/{image_url}"

    async def create(self, session_id: str = "demo-session") -> CartView:
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self._config.cart_ttl_hours
        )
        cart = await self._repository.create(session_id, "northstar", expires_at)
        return await self._to_view(cart)

    async def get(self, cart_id: UUID) -> CartView:
        cart = await self._repository.require(cart_id)
        return await self._to_view(cart)

    async def add(self, cart_id: UUID, request: AddCartItemRequest) -> CartView:
        cart = await self._repository.require(cart_id)
        snapshot = await self._inventory.variant_snapshot(
            request.variant_id,
            request.branch_id,
            self._resolve_image_url,
        )
        current_quantity = sum(
            item.quantity
            for item in cart.items
            if item.variant_id == request.variant_id
            and item.branch_id == request.branch_id
        )
        requested_total = current_quantity + request.quantity
        if snapshot.available_quantity < requested_total:
            raise ConflictError("The requested quantity is no longer available.", code="OUT_OF_STOCK")
            
        updated = await self._repository.add_or_increment(
            cart_id,
            snapshot.product_id,
            request.variant_id,
            request.branch_id,
            request.quantity,
        )
        return await self._to_view(updated)

    async def update(self, cart_id: UUID, item_id: UUID, quantity: int) -> CartView:
        cart = await self._repository.require(cart_id)
        item = next((i for i in cart.items if i.item_id == item_id), None)
        if not item:
            raise ConflictError("Item not found.", code="ITEM_NOT_FOUND")
            
        snapshot = await self._inventory.variant_snapshot(item.variant_id, item.branch_id, self._resolve_image_url)
        if snapshot.available_quantity < quantity:
            raise ConflictError("The requested quantity is no longer available.", code="OUT_OF_STOCK")
            
        updated = await self._repository.update_quantity(cart_id, item_id, quantity)
        return await self._to_view(updated)

    async def remove(self, cart_id: UUID, item_id: UUID) -> CartView:
        updated = await self._repository.remove_item(cart_id, item_id)
        return await self._to_view(updated)

    async def clear(self, cart_id: UUID) -> CartView:
        updated = await self._repository.clear(cart_id)
        return await self._to_view(updated)

    async def preview(self, cart_id: UUID, request: PreviewCartRequest) -> StoreOrderPreview:
        cart = await self._repository.require(cart_id)
        view = await self._to_view(cart)
        
        discount = await self._promotions.calculate_discount(
            view.subtotal,
            view.items,
            request.offer_code
        )
        
        delivery_fee = Decimal("15.00") if view.subtotal > 0 and view.subtotal < Decimal("100.00") else Decimal("0.00")
        
        grand_total = view.subtotal - discount + delivery_fee
        
        return StoreOrderPreview(
            cart_id=view.cart_id,
            items=view.items,
            total_quantity=view.total_quantity,
            subtotal=view.subtotal,
            discount_total=discount,
            delivery_fee=delivery_fee,
            grand_total=grand_total,
            applied_offer_code=request.offer_code if discount > 0 else None
        )

    async def _to_view(self, cart: Cart) -> CartView:
        items: list[CartItemView] = []
        subtotal = Decimal("0.00")
        total_quantity = 0
        
        for item in cart.items:
            snapshot = await self._inventory.variant_snapshot(item.variant_id, item.branch_id, self._resolve_image_url)
            line_total = snapshot.unit_price * item.quantity
            subtotal += line_total
            total_quantity += item.quantity
            
            items.append(
                CartItemView(
                    item_id=item.item_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    branch_id=item.branch_id,
                    article_code=snapshot.article_code,
                    product_name=snapshot.product_name,
                    color=snapshot.color,
                    size=snapshot.size,
                    quantity=item.quantity,
                    unit_price=snapshot.unit_price,
                    line_total=line_total,
                    image_url=snapshot.image_url,
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
