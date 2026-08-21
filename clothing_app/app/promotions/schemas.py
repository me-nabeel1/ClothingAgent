"""Public promotion contracts and evaluation results."""
from decimal import Decimal
from pydantic import BaseModel, Field


class OfferSummary(BaseModel):
    """Customer-safe summary of one offer."""
    offer_code: str
    offer_name: str
    description: str | None
    discount_amount: Decimal | None
    discount_percentage: Decimal | None
    benefit_type: str


class PromotionEvaluation(BaseModel):
    """Authoritative promotion outcome used by catalog and checkout."""
    discount_total: Decimal = Decimal("0.00")
    free_delivery: bool = False
    applied_offers: list[OfferSummary] = Field(default_factory=list)
