"""Transport contracts consumed from the clothing application APIs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OfferSummary(BaseModel):
    offer_code: str
    offer_name: str
    description: str | None = None
    discount_amount: Decimal | None = None
    discount_percentage: Decimal | None = None
    benefit_type: str


class ProductSearchRequest(BaseModel):
    """Structured product-search payload accepted by the clothing application."""

    query_text: str | None = Field(default=None, max_length=300)
    categories: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list, max_length=10)
    excluded_colors: list[str] = Field(default_factory=list, max_length=10)
    size_mapping: dict[str, str] = Field(default_factory=dict, description="Maps category/product_type to desired size, e.g. {'shirts': 'L'}")
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
    """Branch information used for availability filtering."""

    branch_id: int
    branch_code: str
    branch_name: str
    city: str
    address: str
    phone: str | None = None


class BranchAvailabilityView(BaseModel):
    """Stock availability for a specific variant at a specific branch."""
    branch_id: int
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
    """Ranked products returned by the clothing application."""

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


class PreviewCartRequest(BaseModel):
    offer_code: str | None = None


class StoreOrderPreview(BaseModel):
    """The checkout preview with discounts and fees applied."""
    cart_id: UUID
    items: list[CartItemView] = Field(default_factory=list)
    total_quantity: int = 0
    subtotal: Decimal = Decimal("0.00")
    discount_total: Decimal = Decimal("0.00")
    delivery_fee: Decimal = Decimal("0.00")
    grand_total: Decimal = Decimal("0.00")
    applied_offer_code: str | None = None


class PlaceOrderRequest(BaseModel):
    cart_id: UUID
    offer_code: str | None = None
    customer_name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    delivery_address: str
    city: str = Field(max_length=50)
    delivery_notes: str | None = None


class OrderView(BaseModel):
    order_id: UUID
    order_number: str
    status: str
    subtotal: Decimal
    discount_total: Decimal
    delivery_fee: Decimal
    grand_total: Decimal
    applied_offer_code: str | None
    customer_name: str | None
    phone: str | None
    delivery_address: str | None
    city: str | None
    delivery_notes: str | None
    items: list[CartItemView] = Field(default_factory=list)
    created_at: datetime
