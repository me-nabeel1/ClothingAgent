"""Public schemas for orders."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from app.cart.schemas import CartItemView

class PlaceOrderRequest(BaseModel):
    cart_id: UUID
    offer_code: str | None = None
    customer_name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    delivery_address: str
    city: str = Field(max_length=50)
    delivery_notes: str | None = None

class OrderView(BaseModel):
    order_id: UUID
    order_number: str
    status: str
    subtotal: Decimal
    discount_total: Decimal
    delivery_fee: Decimal
    grand_total: Decimal
    applied_offer_code: str | None
    customer_name: str | None
    phone: str | None
    delivery_address: str | None
    city: str | None
    delivery_notes: str | None
    items: list[CartItemView] = Field(default_factory=list)
    created_at: datetime
