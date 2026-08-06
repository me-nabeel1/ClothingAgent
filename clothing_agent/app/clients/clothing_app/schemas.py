"""Transport contracts consumed from the clothing application APIs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductSearchRequest(BaseModel):
    """Structured product-search payload accepted by the clothing application."""

    query_text: str | None = Field(default=None, max_length=300)
    category: str | None = Field(default=None, max_length=100)
    colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    minimum_price: Decimal | None = Field(default=None, ge=0)
    maximum_price: Decimal | None = Field(default=None, ge=0)
    branch_code: str | None = None
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    semantic_tags: list[str] = Field(default_factory=list)
    in_stock_only: bool = True
    allow_relaxation: bool = True
    limit: int = Field(default=8, ge=1, le=30)


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
    """Ranked products returned by the clothing application."""

    products: list[ProductOption] = Field(default_factory=list)
    result_count: int = 0
    relaxed_constraints: list[str] = Field(default_factory=list)


class ProductDetails(BaseModel):
    """Complete product metadata and branch-specific options."""

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


class BranchView(BaseModel):
    """Branch information used for availability filtering."""

    branch_id: int
    branch_code: str
    branch_name: str
    city: str
    address: str
    phone: str | None = None


class AvailabilityView(BaseModel):
    """Current stock for one variant at one branch."""

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


class AddCartItemRequest(BaseModel):
    """Exact branch-specific variant selection."""

    variant_id: int = Field(gt=0)
    branch_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=10)


class UpdateCartItemRequest(BaseModel):
    """Replacement cart-item quantity."""

    quantity: int = Field(ge=1, le=10)


class CartItemView(BaseModel):
    """Trusted cart item returned by the clothing application."""

    item_id: UUID
    product_id: int
    variant_id: int
    branch_id: int
    article_code: str
    product_name: str
    color: str
    size: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    image_url: str | None = None


class CartView(BaseModel):
    """Complete temporary cart."""

    cart_id: UUID
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
