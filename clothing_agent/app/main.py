"""FastAPI entrypoint for the clothing sales-agent service."""

from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_config
from app.core.container import get_container
from app.core.errors import AgentError
from app.core.observability import (
    configure_logging,
    get_request_id,
    reset_request_id,
    set_request_id,
)
from app.core.chat import router as conversation_router

config = get_config()
configure_logging(config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Log lifecycle events and release shared HTTP connections on shutdown."""

    logger.info("agent_started", extra={"event": "agent_started"})
    yield
    await get_container().close()
    logger.info("agent_stopped", extra={"event": "agent_stopped"})


app = FastAPI(
    title=config.app_name,
    version="1.0.0",
    description=(
        "Domain-specific clothing sales concierge with intent routing, "
        "fashion guidance, product retrieval, and cart actions."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(conversation_router, prefix=config.api_prefix)


@app.middleware("http")
async def trace_request(request: Request, call_next):
    """Add a request ID and record latency/status for every agent API call."""

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


@app.get("/health", tags=["health"])
async def health() -> dict[str, object]:
    """Confirm that the agent process and registries are initialized."""

    container = get_container()
    return {
        "status": "ok",
        "service": "clothing-agent",
        "agents": container.agents.names(),
        "tools": container.tools.names(),
        "llm_configured": container.llm.configured,
    }


@app.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, object]:
    """Verify the clothing application and required LLM configuration."""

    container = get_container()
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


@app.exception_handler(AgentError)
async def handle_agent_error(_: Request, exc: AgentError) -> JSONResponse:
    """Log and return one predictable envelope for known agent failures."""

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


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Prevent uncaught request failures from becoming untraceable crashes."""

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
