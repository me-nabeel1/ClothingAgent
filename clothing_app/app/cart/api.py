"""Minimum cart endpoints needed by the demo UI and clothing agent."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.repository import get_cart_repository
from app.cart.schemas import (
    AddCartItemRequest,
    CartView,
    UpdateCartItemRequest,
)
from app.cart.service import CartService
from app.catalog.repository import CatalogRepository
from app.catalog.service import CatalogService
from app.config import get_config
from app.database import get_db

router = APIRouter(prefix="/carts", tags=["cart"])


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    """Compose one request-scoped cart service with catalog validation."""

    return CartService(
        repository=get_cart_repository(),
        catalog=CatalogService(CatalogRepository(db)),
        config=get_config(),
    )


@router.post("", response_model=CartView, status_code=201)
async def create_cart(service: CartService = Depends(get_cart_service)) -> CartView:
    """Create the temporary cart used by chat and normal UI actions."""

    return await service.create()


@router.get("/{cart_id}", response_model=CartView)
async def get_cart(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
) -> CartView:
    """Return the current cart state."""

    return await service.get(cart_id)


@router.post("/{cart_id}/items", response_model=CartView)
async def add_cart_item(
    cart_id: UUID,
    body: AddCartItemRequest,
    service: CartService = Depends(get_cart_service),
) -> CartView:
    """Add an exact branch-specific variant after live validation."""

    return await service.add(cart_id, body)


@router.patch("/{cart_id}/items/{item_id}", response_model=CartView)
async def update_cart_item(
    cart_id: UUID,
    item_id: UUID,
    body: UpdateCartItemRequest,
    service: CartService = Depends(get_cart_service),
) -> CartView:
    """Replace one cart-item quantity."""

    return await service.update(cart_id, item_id, body.quantity)


@router.delete("/{cart_id}/items/{item_id}", response_model=CartView)
async def remove_cart_item(
    cart_id: UUID,
    item_id: UUID,
    service: CartService = Depends(get_cart_service),
) -> CartView:
    """Remove one item from the cart."""

    return await service.remove(cart_id, item_id)


@router.delete("/{cart_id}/items", response_model=CartView)
async def clear_cart(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
) -> CartView:
    """Clear all cart items while retaining the cart identity."""

    return await service.clear(cart_id)
