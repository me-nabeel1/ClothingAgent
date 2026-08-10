"""Public request and response contracts for inventory APIs."""
from decimal import Decimal
from pydantic import BaseModel

class AvailabilityView(BaseModel):
    """Current sellable stock for an exact variant and branch."""
    product_id: int
    variant_id: int
    branch_id: int
    branch_code: str
    branch_name: str
    color: str
    size: str
    price: Decimal
    available_quantity: int
    in_transit_quantity: int
    is_available: bool

class VariantSnapshot(BaseModel):
    """Trusted product facts used by cart operations."""
    product_id: int
    variant_id: int
    branch_id: int
    product_name: str
    article_code: str
    color: str
    size: str
    unit_price: Decimal
    available_quantity: int
    image_url: str | None = None
