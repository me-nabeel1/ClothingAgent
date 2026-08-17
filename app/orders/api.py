"""Public endpoints for placing and viewing orders."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_config
from app.orders.schemas import PlaceOrderRequest, OrderView
from app.orders.repository import OrderRepository
from app.orders.service import OrderService

from app.cart.repository import CartRepository
from app.cart.service import CartService
from app.catalog.repository import CatalogRepository
from app.inventory.service import InventoryService
from app.promotions.repository import PromotionRepository
from app.promotions.service import PromotionService

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    cart_repo = CartRepository(db)
    inventory = InventoryService(CatalogRepository(db))
    promotions = PromotionService(PromotionRepository(db))
    cart_service = CartService(
        repository=cart_repo,
        inventory=inventory,
        promotions=promotions,
        config=get_config(),
    )
    return OrderService(
        repository=OrderRepository(db),
        cart_repo=cart_repo,
        cart_service=cart_service
    )

@router.post("", response_model=OrderView, status_code=201)
async def place_order(
    body: PlaceOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderView:
    """Submit an order and convert the temporary cart to a persistent state."""
    return await service.place_order(body)

@router.get("/{order_id}", response_model=OrderView)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderView:
    """Return an order by ID."""
    return await service.get_order(order_id)
