"""HTTP middleware for observability and tracing."""

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from app.shared.observability import (
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger(__name__)


async def trace_request(request: Request, call_next):
    """Attach a request ID and record API latency and response status."""

    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    token = set_request_id(request_id)
    started = perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )
        return response
    finally:
        reset_request_id(token)
