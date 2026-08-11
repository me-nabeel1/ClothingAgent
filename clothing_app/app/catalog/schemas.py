"""Public request and response contracts for catalog and inventory APIs."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


from app.promotions.schemas import OfferSummary


class ProductSearchRequest(BaseModel):
    """Structured search criteria accepted from the UI or clothing agent."""

    query_text: str | None = Field(default=None, max_length=300)
    categories: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list, max_length=10)
    excluded_colors: list[str] = Field(default_factory=list, max_length=10)
    sizes: list[str] = Field(default_factory=list, max_length=10)
    excluded_product_ids: list[int] = Field(default_factory=list)
    minimum_price: Decimal | None = Field(default=None, ge=0)
    maximum_price: Decimal | None = Field(default=None, ge=0)
    branch_code: str | None = Field(default=None, max_length=30)
    materials: list[str] = Field(default_factory=list, max_length=10)
    fits: list[str] = Field(default_factory=list, max_length=10)
    seasons: list[str] = Field(default_factory=list, max_length=10)
    semantic_tags: list[str] = Field(default_factory=list, max_length=20)
    article_code: str | None = Field(default=None, max_length=40)
    sku: str | None = Field(default=None, max_length=80)
    in_stock_only: bool = True
    allow_relaxation: bool = True
    limit: int = Field(default=20, ge=1, le=20)


class BranchView(BaseModel):
    """Branch information needed by product and availability displays."""

    branch_id: int
    branch_code: str
    branch_name: str
    city: str
    address: str


class BranchAvailabilityView(BaseModel):
    """Stock availability for a specific variant at a specific branch."""
    branch_code: str
    branch_name: str
    is_available: bool
    available_quantity: int


class VariantView(BaseModel):
    """A specific size and color combination for a product."""
    variant_id: int
    sku: str
    color: str
    size: str
    price: Decimal
    final_price: Decimal
    discount_amount: Decimal = Field(default=Decimal("0.00"))
    applied_offer: OfferSummary | None = None
    is_available: bool
    branch_availability: list[BranchAvailabilityView] = Field(default_factory=list)


class ProductView(BaseModel):
    """A complete product response containing all variants and capabilities."""
    product_id: int
    article_code: str
    product_name: str
    description: str | None = None
    category: str
    subcategory: str | None = None
    product_type: str
    gender: str
    brand: str
    material: str | None = None
    fit: str | None = None
    season: str | None = None
    occasion: str | None = None
    base_price: Decimal
    final_price: Decimal
    discount_amount: Decimal = Field(default=Decimal("0.00"))
    applied_offer: OfferSummary | None = None
    images: list[str] = Field(default_factory=list)
    variants: list[VariantView] = Field(default_factory=list)


class ProductSearchResponse(BaseModel):
    """Ranked product options and transparent relaxation metadata."""

    products: list[ProductView] = Field(default_factory=list)
    result_count: int = 0
    relaxed_constraints: list[str] = Field(default_factory=list)


class ProductDetails(BaseModel):
    """Product metadata and all active branch-specific options."""
    product: ProductView


class MenuCategory(BaseModel):
    category_name: str
    products: list[ProductView]

class MenuResponse(BaseModel):
    categories: list[MenuCategory]

class StoreContext(BaseModel):
    """General capabilities and catalog structure for the Agent."""
    store_name: str
    store_id: str
    branches: list[BranchView]
    categories: list[str]
    subcategories: list[str]
    product_types: list[str]
    supported_attributes: list[str]
    sizes: list[str]
    colors: list[str]
    seasons: list[str]
    occasions: list[str]
    capabilities: list[str]
