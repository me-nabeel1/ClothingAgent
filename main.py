"""Single-port FastAPI application consolidating Clothing App catalog and Sales Concierge agent."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_config
from app.core.container import get_container
from app.core.errors import AgentError
from app.core.exception_handlers import handle_agent_error, handle_unexpected_error
from app.core.middleware import trace_request
from app.core.observability import configure_logging

# Agent Chat
from app.core.chat import router as chat_router

# Catalog Domain Routers
from app.catalog.api import router as catalog_router
from app.cart.api import router as cart_router
from app.orders.api import router as orders_router
from app.inventory.api import router as inventory_router
from app.promotions.api import router as promotions_router

config = get_config()
configure_logging(config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources."""
    logger.info("unified_service_started", extra={"event": "unified_service_started"})

    # Automatically ensure schema and all database tables exist on FastAPI startup
    try:
        from sqlalchemy import text
        from app.database import Base, get_engine
        from app.catalog.models import Branch, Category, Product, ProductVariant, Color, Size, ProductImage
        from app.inventory.models import BranchInventory
        from app.promotions.models import Offer
        from app.cart.models import Cart, CartItem
        from app.orders.models import Order, OrderItem

        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS clothing_store;"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_ensured", extra={"event": "database_tables_ensured"})
    except Exception as exc:
        logger.warning(f"Database schema startup initialization skipped: {exc}")

    try:
        yield
    finally:
        await get_container().close()
        logger.info("unified_service_stopped", extra={"event": "unified_service_stopped"})


app = FastAPI(
    title="Clothing Sales Concierge & Catalog Microservice",
    version="1.0.0",
    description="Unified single-port service combining catalog APIs and AI sales concierge.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Consolidated API Endpoints (/api/v1)
# ------------------------------------------------------------------
app.include_router(chat_router, prefix=config.api_prefix)       # /api/v1/chat (Agent Concierge)
app.include_router(catalog_router, prefix=config.api_prefix)    # /api/v1/products (Catalog)
app.include_router(cart_router, prefix=config.api_prefix)       # /api/v1/carts (Cart Management)
app.include_router(orders_router, prefix=config.api_prefix)     # /api/v1/orders (Checkout & Orders)
app.include_router(inventory_router, prefix=config.api_prefix)  # /api/v1/inventory (Stock & Branches)
app.include_router(promotions_router, prefix=config.api_prefix) # /api/v1/promotions (Discounts & Offers)

# Backwards compatibility fallback routes (Hidden from Swagger UI)
from app.catalog.api import get_menu as catalog_get_menu
app.add_api_route("/menu", catalog_get_menu, methods=["GET"], include_in_schema=False)
app.add_api_route("/catalog/menu", catalog_get_menu, methods=["GET"], include_in_schema=False)
app.add_api_route("/catalog/api/v1/menu", catalog_get_menu, methods=["GET"], include_in_schema=False)

# ------------------------------------------------------------------
# Static Assets (Product Images)
# ------------------------------------------------------------------
img_dir = Path("local/product_images")
if img_dir.exists():
    app.mount("/assets/products", StaticFiles(directory=str(img_dir)), name="product_images")

# ------------------------------------------------------------------
# Root Health & Global Error Handling
# ------------------------------------------------------------------
@app.get("/health")
async def root_health():
    return {"status": "ok", "service": "clothing-unified-microservice", "port": 8000}

app.middleware("http")(trace_request)
app.exception_handler(AgentError)(handle_agent_error)
app.exception_handler(Exception)(handle_unexpected_error)
