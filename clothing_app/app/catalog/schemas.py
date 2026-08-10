"""Public request and response contracts for catalog and inventory APIs."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ProductSearchRequest(BaseModel):
    """Structured search criteria accepted from the UI or clothing agent."""

    query_text: str | None = Field(default=None, max_length=300)
    category: str | None = Field(default=None, max_length=100)
    colors: list[str] = Field(default_factory=list, max_length=10)
    excluded_colors: list[str] = Field(default_factory=list, max_length=10)
    sizes: list[str] = Field(default_factory=list, max_length=10)
    excluded_product_ids: list[int] = Field(default_factory=list)
    minimum_price: Decimal | None = Field(default=None, ge=0)
    maximum_price: Decimal | None = Field(default=None, ge=0)
    branch_code: str | None = Field(default=None, max_length=30)
    materials: list[str] = Field(default_factory=list, max_length=10)
    fits: list[str] = Field(default_factory=list, max_length=10)
    semantic_tags: list[str] = Field(default_factory=list, max_length=20)
    in_stock_only: bool = True
    allow_relaxation: bool = True
    limit: int = Field(default=8, ge=1, le=30)


class BranchView(BaseModel):
    """Branch information needed by product and availability displays."""

    branch_id: int
    branch_code: str
    branch_name: str
    city: str
    address: str


class ProductOption(BaseModel):
    """One exact product variant at one branch."""

    product_id: int
    variant_id: int
    branch_id: int
    article_code: str
    product_name: str
    category: str
    gender: str
    brand: str
    color: str
    size: str
    price: Decimal
    branch_code: str
    branch_name: str
    city: str
    available_quantity: int
    in_transit_quantity: int = 0
    image_url: str | None = None
    material: str | None = None
    fit: str | None = None
    season: str | None = None
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    match_score: float = 0
    match_reasons: list[str] = Field(default_factory=list)


class ProductSearchResponse(BaseModel):
    """Ranked product options and transparent relaxation metadata."""

    products: list[ProductOption] = Field(default_factory=list)
    result_count: int = 0
    relaxed_constraints: list[str] = Field(default_factory=list)


class ProductDetails(BaseModel):
    """Product metadata and all active branch-specific options."""

    product_id: int
    article_code: str
    product_name: str
    category: str
    gender: str
    brand: str
    material: str | None = None
    fit: str | None = None
    season: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    attributes: dict[str, object] = Field(default_factory=dict)
    image_urls: list[str] = Field(default_factory=list)
    options: list[ProductOption] = Field(default_factory=list)


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
    image_url: str | None = None

class MenuCategory(BaseModel):
    category_name: str
    products: list[ProductOption]

class MenuResponse(BaseModel):
    categories: list[MenuCategory]
