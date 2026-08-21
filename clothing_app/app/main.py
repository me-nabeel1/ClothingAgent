"""FastAPI entrypoint for the clothing-application demonstration service."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import handle_app_error, handle_unexpected_error
from app.api.health import router as health_router
from app.api.middleware import trace_request
from app.cart.api import router as cart_router
from app.catalog.api import router as catalog_router
from app.inventory.api import router as inventory_router
from app.promotions.api import router as promotions_router
from app.orders.api import router as orders_router
from app.config import get_config
from app.database import close_database
from app.common.exceptions import AppError
from app.common.observability import configure_logging

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
app.include_router(inventory_router, prefix=config.api_prefix)
app.include_router(promotions_router, prefix=config.api_prefix)
app.include_router(cart_router, prefix=config.api_prefix)
app.include_router(orders_router, prefix=config.api_prefix)
app.include_router(health_router)

images_dir = Path(config.product_images_dir)
if images_dir.exists():
    app.mount("/assets/products", StaticFiles(directory=images_dir), name="product-images")


app.middleware("http")(trace_request)
app.exception_handler(AppError)(handle_app_error)
app.exception_handler(Exception)(handle_unexpected_error)
