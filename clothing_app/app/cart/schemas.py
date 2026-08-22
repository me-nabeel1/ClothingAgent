"""Public request and response contracts for carts."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class CreateCartRequest(BaseModel):
    """Optional client session/store context used to create or reuse a cart."""
    session_id: str | None = Field(default=None, min_length=1, max_length=120)
    store_id: str | None = Field(default=None, min_length=1, max_length=50)


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
    category_id: int | None = None
    color: str
    size: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    image_url: str | None = None


class CartView(BaseModel):
    """Complete cart returned to the UI and clothing agent."""
    cart_id: UUID
    session_id: str
    store_id: str
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


class PreviewCartRequest(BaseModel):
    """Optional checkout offer code."""
    offer_code: str | None = None


class StoreOrderPreview(BaseModel):
    """Authoritative checkout preview with discount and delivery effects."""
    cart_id: UUID
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    discount_total: Decimal = Decimal("0.00")
    delivery_fee: Decimal = Decimal("0.00")
    grand_total: Decimal = Decimal("0.00")
    applied_offer_code: str | None = None
    applied_offer_codes: list[str] = Field(default_factory=list)
    free_delivery: bool = False
    confirmation_token: UUID | None = None
