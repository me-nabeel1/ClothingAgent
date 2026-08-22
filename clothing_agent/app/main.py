"""FastAPI entrypoint for the clothing sales-agent service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.chat import router as conversation_router
from app.core.config import get_config
from app.core.container import get_container
from app.core.errors import AgentError
from app.core.exception_handlers import handle_agent_error, handle_unexpected_error
from app.core.health import router as health_router
from app.core.middleware import trace_request
from app.core.observability import configure_logging

config = get_config()
configure_logging(config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage agent resources during application startup and shutdown."""
    logger.info("agent_started", extra={"event": "agent_started"})
    try:
        yield
    finally:
        await get_container().close()
        logger.info("agent_stopped", extra={"event": "agent_stopped"})


app = FastAPI(
    title=config.app_name,
    version="1.0.0",
    description=(
        "Domain-specific clothing sales concierge with guided discovery, "
        "catalog retrieval, and cart actions."
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
from app.api.routes import router as agent_router, get_agent

app.include_router(agent_router)
app.include_router(conversation_router, prefix=config.api_prefix)
app.include_router(health_router)

app.dependency_overrides[get_agent] = lambda: get_container().fitzy_agent

app.middleware("http")(trace_request)
app.exception_handler(AgentError)(handle_agent_error)
app.exception_handler(Exception)(handle_unexpected_error)
