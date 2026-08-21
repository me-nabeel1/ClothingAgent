"""Public endpoints for promotions."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.promotions.schemas import OfferSummary
from app.promotions.repository import PromotionRepository
from app.promotions.service import PromotionService

router = APIRouter(tags=["promotions"])

def get_promotion_service(db: AsyncSession = Depends(get_db)) -> PromotionService:
    return PromotionService(PromotionRepository(db))

@router.get("/promotions", response_model=list[OfferSummary])
async def list_active_promotions(
    service: PromotionService = Depends(get_promotion_service),
) -> list[OfferSummary]:
    """List all active store-wide and global promotions."""
    return await service.get_active_offers_summary()
