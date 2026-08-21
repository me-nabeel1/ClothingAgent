"""Inventory endpoints for availability and stock checks."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.schemas import AvailabilityView
from app.inventory.service import InventoryService
from app.inventory.repository import InventoryRepository
from app.database import get_db

router = APIRouter(tags=["inventory"])

def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(InventoryRepository(db))

@router.get("/inventory/availability", response_model=AvailabilityView)
async def get_availability(
    variant_id: int = Query(gt=0),
    branch_id: int = Query(gt=0),
    service: InventoryService = Depends(get_inventory_service),
) -> AvailabilityView:
    """Return live availability for one exact variant and branch."""
    return await service.get_availability(variant_id, branch_id)
