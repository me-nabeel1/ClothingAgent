"""Public schemas for orders."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from app.cart.schemas import CartItemView

class PlaceOrderRequest(BaseModel):
    cart_id: UUID
    offer_code: str | None = None

class OrderView(BaseModel):
    order_id: UUID
    order_number: str
    status: str
    subtotal: Decimal
    discount_total: Decimal
    delivery_fee: Decimal
    grand_total: Decimal
    applied_offer_code: str | None
    items: list[CartItemView] = Field(default_factory=list)
    created_at: datetime
