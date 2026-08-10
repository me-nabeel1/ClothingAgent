"""Common input and output contracts for all specialist agents."""

from __future__ import annotations

from typing import Any

from app.clients.clothing_app.schemas import CartView, ProductOption
from app.core.conversation import ConversationState
from app.core.routing import RouteDecision
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Context supplied to one selected specialist agent."""

    message: str
    context: ConversationState
    route: RouteDecision


class AgentResult(BaseModel):
    """Unified result returned by every specialist agent."""

    reply: str
    products: list[ProductOption] = Field(default_factory=list)
    cart: CartView | None = None
    suggested_actions: list[str] = Field(default_factory=list)
    ui_actions: list[str] = Field(default_factory=list)
    state_updates: dict[str, Any] = Field(default_factory=dict)
