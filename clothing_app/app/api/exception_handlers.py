"""Exception handlers for the clothing application APIs."""

import logging

from app.shared.errors import AppError
from app.shared.observability import get_request_id
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    """Log and return one predictable envelope for domain failures."""

    logger.warning(
        "clothing_app_error",
        extra={
            "event": "clothing_app_error",
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
                "request_id": get_request_id(),
            }
        },
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected database/API errors and return a traceable response."""

    logger.exception(
        "unhandled_clothing_app_error",
        extra={
            "event": "unhandled_clothing_app_error",
            "method": request.method,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_CLOTHING_APP_ERROR",
                "message": "The clothing application could not complete this request.",
                "request_id": get_request_id(),
            }
        },
    )
