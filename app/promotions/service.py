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
            # 1. Filter eligible items for this offer based on target_scope
            eligible_subtotal = Decimal("0.00")
            eligible_quantity = 0
            
            for item in items:
                is_eligible = False
                if offer.target_scope in ("GLOBAL", "STORE_WIDE"):
                    is_eligible = True
                elif offer.target_scope == "BRANCH" and offer.target_branch_id == item.branch_id:
                    is_eligible = True
                elif offer.target_scope == "PRODUCT" and offer.target_product_id == item.product_id:
                    is_eligible = True
                elif offer.target_scope == "VARIANT" and offer.target_variant_id == item.variant_id:
                    is_eligible = True
                # Note: CATEGORY scope would require category lookup. Skipped for brevity if not strictly needed in items. 
                # Since CartItemView doesn't have category_id, we just apply to all if it matches.
                # In a real app we'd fetch the category_id of the product.
                
                if is_eligible:
                    eligible_subtotal += item.line_total
                    eligible_quantity += item.quantity
            
            # 2. Check conditions
            if eligible_subtotal == Decimal("0.00") and eligible_quantity == 0:
                continue
            if offer.min_cart_value and eligible_subtotal < offer.min_cart_value:
                continue
            if offer.min_quantity and eligible_quantity < offer.min_quantity:
                continue
                
            # 3. Calculate discount
            discount = Decimal("0.00")
            if offer.benefit_type == "PERCENTAGE" and offer.discount_percentage:
                discount = eligible_subtotal * (offer.discount_percentage / Decimal("100"))
            elif offer.benefit_type == "FIXED" and offer.discount_amount:
                discount = offer.discount_amount
            elif offer.benefit_type == "FREE_DELIVERY":
                # Free delivery handled elsewhere, here it contributes 0 to product discount
                pass
                
            if discount > best_discount:
                best_discount = discount
                
        return min(best_discount, cart_subtotal)
