"""Public request and response contracts for temporary carts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AddCartItemRequest(BaseModel):
    """Exact variant selection accepted when adding an item."""

    variant_id: int = Field(gt=0)
    branch_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=10)


class UpdateCartItemRequest(BaseModel):
    """Replacement quantity for one cart item."""

    quantity: int = Field(ge=1, le=10)


class CartItemView(BaseModel):
    """Trusted cart item populated from catalog data, not client prices."""

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
    line_total: Decimal
    image_url: str | None = None


class CartView(BaseModel):
    """Complete temporary cart returned to the UI and clothing agent."""

    cart_id: UUID
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

class PreviewCartRequest(BaseModel):
    offer_code: str | None = None

class StoreOrderPreview(BaseModel):
    """The checkout preview with discounts and fees applied."""
    cart_id: UUID
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    discount_total: Decimal = Decimal("0.00")
    delivery_fee: Decimal = Decimal("0.00")
    grand_total: Decimal = Decimal("0.00")
    applied_offer_code: str | None = None
