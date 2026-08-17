"""Exception handlers for the agent API."""

import logging

from app.core.errors import AgentError
from app.core.observability import get_request_id
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def handle_agent_error(_: Request, exc: AgentError) -> JSONResponse:
    logger.warning(
        "agent_error",
        extra={
            "event": "agent_error",
            "error_code": exc.code,
            "status_code": exc.status_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": get_request_id(),
            }
        },
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_agent_error",
        extra={
            "event": "unhandled_agent_error",
            "method": request.method,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_AGENT_ERROR",
                "message": "The agent could not complete this request.",
                "request_id": get_request_id(),
            }
        },
    )
