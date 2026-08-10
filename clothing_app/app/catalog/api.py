"""Read-only catalog and inventory endpoints used by the demo application."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.repository import CatalogRepository
from app.catalog.schemas import (
    AvailabilityView,
    BranchView,
    ProductDetails,
    ProductSearchRequest,
    ProductSearchResponse,
    MenuResponse,
)
from app.catalog.service import CatalogService
from app.database import get_db

router = APIRouter(tags=["catalog"])


def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    """Compose a request-scoped catalog service."""

    return CatalogService(CatalogRepository(db))

@router.get("/menu", response_model=MenuResponse)
async def get_menu(
    service: CatalogService = Depends(get_catalog_service),
) -> MenuResponse:
    """Return a menu of products grouped by predefined categories."""
    menu = await service.get_menu()
    return MenuResponse(categories=menu)


@router.get("/products", response_model=ProductSearchResponse)
async def list_products(
    query_text: str | None = Query(default=None, max_length=300),
    category: str | None = Query(default=None, max_length=100),
    color: list[str] | None = Query(default=None),
    size: list[str] | None = Query(default=None),
    minimum_price: Decimal | None = Query(default=None, ge=0),
    maximum_price: Decimal | None = Query(default=None, ge=0),
    branch_code: str | None = Query(default=None, max_length=30),
    in_stock_only: bool = True,
    limit: int = Query(default=12, ge=1, le=30),
    service: CatalogService = Depends(get_catalog_service),
) -> ProductSearchResponse:
    """List products with optional filters for normal non-chat browsing."""

    return await service.search(
        ProductSearchRequest(
            query_text=query_text,
            category=category,
            colors=color or [],
            sizes=size or [],
            minimum_price=minimum_price,
            maximum_price=maximum_price,
            branch_code=branch_code,
            in_stock_only=in_stock_only,
            allow_relaxation=False,
            limit=limit,
        )
    )


@router.post("/products/search", response_model=ProductSearchResponse)
async def search_products(
    body: ProductSearchRequest,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductSearchResponse:
    """Run the structured search contract used by the future clothing agent."""

    return await service.search(body)


@router.get("/products/{product_id}", response_model=ProductDetails)
async def get_product(
    product_id: int,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductDetails:
    """Return full product details and available color/size/branch options."""

    return await service.get_product(product_id)


@router.get("/branches", response_model=list[BranchView])
async def list_branches(
    service: CatalogService = Depends(get_catalog_service),
) -> list[BranchView]:
    """Return active branches available for product filtering."""

    return await service.list_branches()


@router.get("/inventory/availability", response_model=AvailabilityView)
async def get_availability(
    variant_id: int = Query(gt=0),
    branch_id: int = Query(gt=0),
    service: CatalogService = Depends(get_catalog_service),
) -> AvailabilityView:
    """Return live availability for one exact variant and branch."""

    return await service.get_availability(variant_id, branch_id)
