"""Pure contract tests for backend hardening rules."""
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.catalog.schemas import ProductSearchRequest
from app.promotions.service import PromotionService


def test_search_rejects_invalid_price_range() -> None:
    with pytest.raises(ValueError):
        ProductSearchRequest(minimum_price=Decimal("5000"), maximum_price=Decimal("4000"))


def test_category_promotion_is_evaluated() -> None:
    offer = SimpleNamespace(
        target_scope="CATEGORY",
        target_category_id=7,
        target_branch_id=None,
        target_product_id=None,
        target_variant_id=None,
        min_cart_value=None,
        min_quantity=None,
        benefit_type="PERCENTAGE",
        discount_percentage=Decimal("20"),
        discount_amount=None,
        stacking_policy="EXCLUSIVE",
        offer_code="CAT20",
        offer_name="Category 20%",
        description="",
    )
    result = PromotionService.best_variant_offer(
        [offer], product_id=1, variant_id=2, branch_id=3,
        category_id=7, base_price=Decimal("5000.00"),
    )
    assert result.discount_total == Decimal("1000.00")
    assert result.applied_offers[0].offer_code == "CAT20"


def test_free_delivery_is_not_treated_as_product_discount() -> None:
    offer = SimpleNamespace(
        target_scope="STORE_WIDE",
        target_category_id=None,
        target_branch_id=None,
        target_product_id=None,
        target_variant_id=None,
        min_cart_value=None,
        min_quantity=None,
        benefit_type="FREE_DELIVERY",
        discount_percentage=None,
        discount_amount=None,
        stacking_policy="STACK",
        offer_code="FREESHIP",
        offer_name="Free Delivery",
        description="",
    )
    result = PromotionService.best_variant_offer(
        [offer], product_id=1, variant_id=2, branch_id=3,
        category_id=7, base_price=Decimal("5000.00"),
    )
    assert result.discount_total == Decimal("0.00")
    assert not result.applied_offers


def test_promotion_fixed_discount_is_capped_to_eligible_amount() -> None:
    offer = SimpleNamespace(
        target_scope="STORE_WIDE",
        target_category_id=None,
        target_branch_id=None,
        target_product_id=None,
        target_variant_id=None,
        min_cart_value=None,
        min_quantity=None,
        benefit_type="FIXED",
        discount_percentage=None,
        discount_amount=Decimal("2000"),
        stacking_policy="EXCLUSIVE",
        offer_code="SAVE2000",
        offer_name="Save 2000",
        description="",
    )
    result = PromotionService.best_variant_offer(
        [offer], product_id=1, variant_id=2, branch_id=3,
        category_id=7, base_price=Decimal("1000.00"),
    )
    assert result.discount_total == Decimal("1000.00")
