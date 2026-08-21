"""SQLAlchemy repository for promotions."""
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.promotions.models import Offer
from app.config import get_config

class PromotionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_active_offers(self) -> list[Offer]:
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(Offer).where(
                Offer.is_active.is_(True),
                Offer.store_id == get_config().store_id,
                Offer.valid_from <= now,
                (Offer.valid_until.is_(None)) | (Offer.valid_until > now)
            ).order_by(Offer.priority.desc())
        )
        return list(result.scalars().all())

    async def get_offer_by_code(self, offer_code: str) -> Offer | None:
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(Offer).where(
                Offer.offer_code == offer_code,
                Offer.store_id == get_config().store_id,
                Offer.is_active.is_(True),
                Offer.store_id == get_config().store_id,
                Offer.valid_from <= now,
                (Offer.valid_until.is_(None)) | (Offer.valid_until > now)
            )
        )
        return result.scalars().first()

    @property
    def db(self) -> AsyncSession:
        """Return the active session for read-only promotion lookups."""
        return self._db
