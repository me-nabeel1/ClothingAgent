"""Health and readiness checks for the clothing application."""

import logging

from app.catalog.models import Branch, Product
from app.database import get_session_factory
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Confirm that the FastAPI process is running."""

    return {"status": "ok", "service": "clothing-app"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    """Verify connectivity and the minimum catalog schema used by the APIs."""

    try:
        async with get_session_factory()() as db:
            await db.execute(select(Branch.branch_id).limit(1))
            await db.execute(select(Product.product_id).limit(1))
    except Exception as exc:
        logger.exception("database_readiness_failed", extra={"event": "database_readiness_failed"})
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "database": "unavailable_or_schema_mismatch"},
        ) from exc

    return {"status": "ready", "database": "connected"}
