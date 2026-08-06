"""FastAPI entrypoint for the clothing-application demonstration service."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.cart.api import router as cart_router
from app.catalog.api import router as catalog_router
from app.catalog.models import Branch, Product
from app.config import get_config
from app.database import close_database, get_session_factory
from app.shared.errors import AppError
from app.shared.observability import (
    configure_logging,
    get_request_id,
    reset_request_id,
    set_request_id,
)

config = get_config()
configure_logging(config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Log lifecycle events and release PostgreSQL connections on shutdown."""

    logger.info("clothing_app_started", extra={"event": "clothing_app_started"})
    yield
    await close_database()
    logger.info("clothing_app_stopped", extra={"event": "clothing_app_stopped"})


app = FastAPI(
    title=config.app_name,
    version="1.0.0",
    description=(
        "Minimal clothing-application APIs for local product retrieval, "
        "inventory availability, and temporary demo-cart actions."
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

app.include_router(catalog_router, prefix=config.api_prefix)
app.include_router(cart_router, prefix=config.api_prefix)

images_dir = Path(config.product_images_dir)
if images_dir.exists():
    app.mount("/assets/products", StaticFiles(directory=images_dir), name="product-images")


@app.middleware("http")
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


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Confirm that the FastAPI process is running."""

    return {"status": "ok", "service": "clothing-app"}


@app.get("/health/ready", tags=["health"])
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


@app.exception_handler(AppError)
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


@app.exception_handler(Exception)
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
