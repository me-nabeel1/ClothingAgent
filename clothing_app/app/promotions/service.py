"""Deterministic promotion evaluation shared by catalog and checkout."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from app.catalog.models import Product
from app.promotions.repository import PromotionRepository
from app.promotions.schemas import OfferSummary, PromotionEvaluation


class PromotionService:
    """Evaluate active offers without duplicating business rules across domains."""

    def __init__(self, repository: PromotionRepository) -> None:
        self._repository = repository

    async def get_active_offers_summary(self) -> list[OfferSummary]:
        """Return customer-safe summaries of currently active offers."""
        return [self._summary(o) for o in await self._repository.get_active_offers()]

    async def evaluate_cart(
        self,
        cart_subtotal: Decimal,
        items: list[Any],
        applied_code: str | None = None,
    ) -> PromotionEvaluation:
        """Evaluate all eligible cart offers, including category and free-delivery rules.

        Offers are processed by descending priority. ``EXCLUSIVE`` stops lower-priority
        offers after it is applied; ``STACK`` permits subsequent offers to contribute.
        """
        offers = await self._repository.get_active_offers()
        if applied_code:
            offers = [o for o in offers if o.offer_code.lower() == applied_code.lower()]

        product_category_ids = await self._category_ids({item.product_id for item in items})
        evaluation = PromotionEvaluation()
        effective_subtotal = Decimal("0.00")

        for offer in offers:
            eligible_subtotal = Decimal("0.00")
            eligible_quantity = 0
            for item in items:
                if self._eligible(offer, item, product_category_ids):
                    eligible_subtotal += Decimal(item.line_total)
                    eligible_quantity += int(item.quantity)

            if eligible_quantity == 0:
                continue
            if offer.min_cart_value is not None and eligible_subtotal < offer.min_cart_value:
                continue
            if offer.min_quantity is not None and eligible_quantity < offer.min_quantity:
                continue

            summary = self._summary(offer)
            if offer.benefit_type == "FREE_DELIVERY":
                evaluation.free_delivery = True
            else:
                discount = self._discount_for_offer(offer, eligible_subtotal)
                if discount > 0:
                    evaluation.discount_total += discount
            evaluation.applied_offers.append(summary)
            effective_subtotal += eligible_subtotal

            if offer.stacking_policy.upper() == "EXCLUSIVE":
                break

        evaluation.discount_total = min(
            evaluation.discount_total.quantize(Decimal("0.01")),
            cart_subtotal,
        )
        return evaluation

    async def evaluate_variant(
        self,
        *,
        product_id: int,
        variant_id: int,
        branch_id: int,
        base_price: Decimal,
    ) -> PromotionEvaluation:
        """Evaluate product-display-safe promotions for one variant."""
        offers = await self._repository.get_active_offers()
        category_ids = await self._category_ids({product_id})
        category_id = category_ids.get(product_id)
        return self.best_variant_offer(
            offers, product_id=product_id, variant_id=variant_id, branch_id=branch_id,
            category_id=category_id, base_price=base_price,
        )

    @classmethod
    def best_variant_offer(
        cls,
        offers: list[Any],
        *,
        product_id: int,
        variant_id: int,
        branch_id: int,
        category_id: int | None,
        base_price: Decimal,
    ) -> PromotionEvaluation:
        """Evaluate display-safe offers against already-loaded active offers."""
        result = PromotionEvaluation()
        for offer in offers:
            if offer.min_cart_value not in (None, Decimal("0.00")):
                continue
            if offer.min_quantity not in (None, 0, 1):
                continue
            scope = offer.target_scope.upper()
            eligible = (
                scope in {"GLOBAL", "STORE_WIDE"}
                or (scope == "BRANCH" and offer.target_branch_id == branch_id)
                or (scope == "PRODUCT" and offer.target_product_id == product_id)
                or (scope == "VARIANT" and offer.target_variant_id == variant_id)
                or (scope == "CATEGORY" and offer.target_category_id == category_id)
            )
            if not eligible or offer.benefit_type == "FREE_DELIVERY":
                continue
            discount = cls._discount_for_offer(offer, base_price)
            if discount > result.discount_total:
                result.discount_total = discount
                result.applied_offers = [cls._summary(offer)]
        return result

    async def _category_ids(self, product_ids: set[int]) -> dict[int, int]:
        """Load product-category relationships once per evaluation."""
        if not product_ids:
            return {}
        result = await self._repository.db.execute(
            select(Product.product_id, Product.category_id).where(Product.product_id.in_(product_ids))
        )
        return {int(row.product_id): int(row.category_id) for row in result}

    @staticmethod
    def _eligible(offer: Any, item: Any, category_ids: dict[int, int]) -> bool:
        """Return whether an offer targets the given cart/product context."""
        scope = offer.target_scope.upper()
        return (
            scope in {"GLOBAL", "STORE_WIDE"}
            or (scope == "BRANCH" and offer.target_branch_id == item.branch_id)
            or (scope == "PRODUCT" and offer.target_product_id == item.product_id)
            or (scope == "VARIANT" and offer.target_variant_id == item.variant_id)
            or (scope == "CATEGORY" and offer.target_category_id == category_ids.get(item.product_id))
        )

    @staticmethod
    def _discount_for_offer(offer: Any, amount: Decimal) -> Decimal:
        """Calculate one offer's product discount using Decimal arithmetic."""
        if offer.benefit_type == "PERCENTAGE" and offer.discount_percentage:
            return (amount * (offer.discount_percentage / Decimal("100"))).quantize(Decimal("0.01"))
        if offer.benefit_type == "FIXED" and offer.discount_amount:
            return min(Decimal(offer.discount_amount), amount)
        return Decimal("0.00")

    @staticmethod
    def _summary(offer: Any) -> OfferSummary:
        """Convert an ORM offer to the stable API summary."""
        return OfferSummary(
            offer_code=offer.offer_code,
            offer_name=offer.offer_name,
            description=offer.description,
            discount_amount=offer.discount_amount,
            discount_percentage=offer.discount_percentage,
            benefit_type=offer.benefit_type,
        )

    async def calculate_discount(self, cart_subtotal: Decimal, items: list[Any], applied_code: str | None = None) -> Decimal:
        """Backward-compatible scalar wrapper around :meth:`evaluate_cart`."""
        evaluation = await self.evaluate_cart(cart_subtotal, items, applied_code)
        return evaluation.discount_total

    @property
    def repository(self) -> PromotionRepository:
        """Expose the repository only to composition code that needs it."""
        return self._repository
