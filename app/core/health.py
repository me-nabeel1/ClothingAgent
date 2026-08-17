"""Health and readiness checks for the agent API."""

import logging

from app.core.config import get_config
from app.core.container import get_container
from app.core.errors import AgentError
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    """Confirm that the agent process and dependencies are initialized."""
    container = get_container()
    return {
        "status": "ok",
        "service": "clothing-agent",
        "agent": "monolithic",
        "llm_configured": container.llm.configured,
    }


@router.get("/health/ready")
async def readiness() -> dict[str, object]:
    """Verify the clothing application and required LLM configuration."""
    container = get_container()
    config = get_config()
    try:
        clothing_app = await container.clothing_app.health()
    except AgentError as exc:
        logger.warning(
            "readiness_dependency_failed",
            extra={"event": "readiness_dependency_failed", "error_code": exc.code},
        )
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "clothing_app": exc.message},
        ) from exc
    if not container.llm.configured and not config.allow_local_fallback:
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "llm": "not_configured"},
        )
    return {
        "status": "ready",
        "clothing_app": clothing_app,
        "llm": "configured" if container.llm.configured else "local_fallback",
    }
