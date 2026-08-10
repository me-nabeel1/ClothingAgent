"""Business logic for evaluating and applying promotional offers."""
from decimal import Decimal
from typing import Any
from app.promotions.repository import PromotionRepository
from app.promotions.schemas import OfferSummary

class PromotionService:
    def __init__(self, repository: PromotionRepository) -> None:
        self._repository = repository

    async def get_active_offers_summary(self) -> list[OfferSummary]:
        offers = await self._repository.get_active_offers()
        return [
            OfferSummary(
                offer_code=o.offer_code,
                offer_name=o.offer_name,
                description=o.description,
                discount_amount=o.discount_amount,
                discount_percentage=o.discount_percentage,
                benefit_type=o.benefit_type
            )
            for o in offers
        ]

    async def calculate_discount(self, cart_subtotal: Decimal, items: list[Any], applied_code: str | None = None) -> Decimal:
        """Calculate the best discount available, optionally applying a specific code."""
        if applied_code:
            offer = await self._repository.get_offer_by_code(applied_code)
            offers = [offer] if offer else []
        else:
            offers = await self._repository.get_active_offers()
            
        if not offers:
            return Decimal("0.00")
            
        best_discount = Decimal("0.00")
        for offer in offers:
            if offer.min_cart_value and cart_subtotal < offer.min_cart_value:
                continue
                
            discount = Decimal("0.00")
            if offer.benefit_type == "PERCENTAGE" and offer.discount_percentage:
                discount = cart_subtotal * (offer.discount_percentage / Decimal("100"))
            elif offer.benefit_type == "FIXED" and offer.discount_amount:
                discount = offer.discount_amount
                
            if discount > best_discount:
                best_discount = discount
                
        return min(best_discount, cart_subtotal)
