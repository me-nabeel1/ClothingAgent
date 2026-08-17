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

# Agent Chat & Health
from app.core.chat import router as chat_router
from app.core.health import router as agent_health_router

# Catalog Domain Routers
from app.api.health import router as catalog_health_router
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
# Catalog Domain Routers (/catalog and root /api/v1)
# ------------------------------------------------------------------
app.include_router(catalog_health_router, prefix="/catalog")
app.include_router(catalog_router, prefix="/catalog/api/v1")
app.include_router(cart_router, prefix="/catalog/api/v1")
app.include_router(orders_router, prefix="/catalog/api/v1")
app.include_router(inventory_router, prefix="/catalog/api/v1")
app.include_router(promotions_router, prefix="/catalog/api/v1")

# Support direct /api/v1 routes for mobile app & ngrok clients
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(promotions_router, prefix="/api/v1")

# ------------------------------------------------------------------
# Agent Concierge Domain Routers (/agent, root /api/v1, and /chat)
# ------------------------------------------------------------------
app.include_router(agent_health_router, prefix="/agent")
app.include_router(chat_router, prefix=f"/agent{config.api_prefix}")
app.include_router(chat_router, prefix=config.api_prefix)
app.include_router(chat_router, prefix="")

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
