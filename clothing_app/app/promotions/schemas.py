"""Public schemas for promotions."""
from decimal import Decimal
from pydantic import BaseModel

class OfferSummary(BaseModel):
    offer_code: str
    offer_name: str
    description: str | None
    discount_amount: Decimal | None
    discount_percentage: Decimal | None
    benefit_type: str
