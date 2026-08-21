"""Public request and response contracts for orders."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.cart.schemas import CartItemView


class PlaceOrderRequest(BaseModel):
    """Customer information and idempotency token required to place one order."""
    cart_id: UUID
    offer_code: str | None = None
    checkout_request_id: str = Field(default_factory=lambda: str(uuid4()), min_length=8, max_length=100)
    customer_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    delivery_address: str = Field(min_length=3)
    city: str = Field(min_length=2, max_length=50)
    delivery_notes: str | None = None


class OrderView(BaseModel):
    """Authoritative placed-order snapshot."""
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
