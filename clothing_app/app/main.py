"""FastAPI entrypoint for the unified Northstar Commerce & Fitzy Sales Agent service."""

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

from clothing_agent.app.api.routes import router as agent_router, chat_router, get_agent
from clothing_agent.app.core.container import get_container
from clothing_agent.app.core.errors import AgentError
from clothing_agent.app.core.exception_handlers import handle_agent_error

config = get_config()
configure_logging(config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Log lifecycle events and release database/container connections on shutdown."""

    logger.info("clothing_app_started", extra={"event": "clothing_app_started"})
    yield
    try:
        await get_container().close()
    except Exception:
        pass
    await close_database()
    logger.info("clothing_app_stopped", extra={"event": "clothing_app_stopped"})


app = FastAPI(
    title="Northstar Menswear Commerce & Fitzy Agent API",
    version="1.0.0",
    description=(
        "Unified FastAPI application serving Northstar Menswear commerce endpoints "
        "and the Fitzy AI Sales Agent."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router, prefix=config.api_prefix)
app.include_router(inventory_router, prefix=config.api_prefix)
app.include_router(promotions_router, prefix=config.api_prefix)
app.include_router(cart_router, prefix=config.api_prefix)
app.include_router(orders_router, prefix=config.api_prefix)
app.include_router(agent_router)
app.include_router(chat_router)
app.include_router(health_router)

app.dependency_overrides[get_agent] = lambda: get_container().fitzy_agent

images_dir = Path(config.product_images_dir)
if images_dir.exists():
    app.mount("/assets/products", StaticFiles(directory=images_dir), name="product-images")


app.middleware("http")(trace_request)
app.exception_handler(AppError)(handle_app_error)
app.exception_handler(AgentError)(handle_agent_error)
app.exception_handler(Exception)(handle_unexpected_error)
