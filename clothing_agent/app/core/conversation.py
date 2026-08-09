"""In-memory conversation state and helpers."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from app.clients.clothing_app.schemas import ProductOption
from app.core.errors import AgentNotFoundError
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    message_id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class DisplayedProduct(BaseModel):
    position: int
    product_id: int
    variant_id: int
    branch_id: int
    product_name: str
    category: str
    color: str
    size: str
    price: Decimal
    branch_name: str


class ShoppingPreferences(BaseModel):
    category: str | None = None
    purpose: str | None = None
    occasion: str | None = None
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    minimum_price: Decimal | None = None
    maximum_price: Decimal | None = None
    branch_code: str | None = None
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    semantic_tags: list[str] = Field(default_factory=list)


class ConversationState(BaseModel):
    conversation_id: UUID
    customer_id: UUID | None = None
    cart_id: UUID | None = None
    messages: list[ConversationMessage] = Field(default_factory=list)
    displayed_products: list[DisplayedProduct] = Field(default_factory=list)
    previous_displayed_products: list[DisplayedProduct] = Field(default_factory=list)
    selected_product: DisplayedProduct | None = None
    preferences: ShoppingPreferences = Field(default_factory=ShoppingPreferences)
    shopping_stage: Literal["new", "clarifying", "ready", "presented", "selected"] = "new"
    clarification_count: int = Field(default=0, ge=0, le=2)
    active_agent: str = "sales_agent"
    current_intent: str = "GENERAL_SHOPPING_HELP"
    created_at: datetime
    updated_at: datetime


class ConversationView(BaseModel):
    conversation_id: UUID
    cart_id: UUID | None = None
    messages: list[ConversationMessage]
    active_agent: str
    current_intent: str
    shopping_stage: str
    created_at: datetime
    updated_at: datetime


class ConversationRepository:
    def __init__(self) -> None:
        self._conversations: dict[UUID, ConversationState] = {}
        self._lock = asyncio.Lock()

    async def create(self) -> ConversationState:
        now = datetime.now(timezone.utc)
        state = ConversationState(
            conversation_id=uuid4(),
            created_at=now,
            updated_at=now,
        )
        async with self._lock:
            self._conversations[state.conversation_id] = state
        return state.model_copy(deep=True)

    async def require(self, conversation_id: UUID) -> ConversationState:
        async with self._lock:
            state = self._conversations.get(conversation_id)
            if not state:
                raise AgentNotFoundError(
                    "Conversation was not found.", code="CONVERSATION_NOT_FOUND"
                )
            return state.model_copy(deep=True)

    async def save(self, state: ConversationState) -> ConversationState:
        state.updated_at = datetime.now(timezone.utc)
        async with self._lock:
            if state.conversation_id not in self._conversations:
                raise AgentNotFoundError(
                    "Conversation was not found.", code="CONVERSATION_NOT_FOUND"
                )
            self._conversations[state.conversation_id] = state.model_copy(deep=True)
        return state.model_copy(deep=True)


class ConversationService:
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    async def create(self) -> ConversationState:
        return await self._repository.create()

    async def get(self, conversation_id: UUID) -> ConversationState:
        return await self._repository.require(conversation_id)

    async def append_message(
        self,
        state: ConversationState,
        *,
        role: str,
        content: str,
    ) -> ConversationState:
        state.messages.append(
            ConversationMessage(
                message_id=uuid4(),
                role=role,  # type: ignore[arg-type]
                content=content,
                created_at=datetime.now(timezone.utc),
            )
        )
        return state

    def set_displayed_products(
        self,
        state: ConversationState,
        products: list[ProductOption],
        *,
        limit: int,
    ) -> None:
        if state.displayed_products:
            state.previous_displayed_products = [
                item.model_copy(deep=True) for item in state.displayed_products
            ]
        state.displayed_products = [
            DisplayedProduct(
                position=index,
                product_id=item.product_id,
                variant_id=item.variant_id,
                branch_id=item.branch_id,
                product_name=item.product_name,
                category=item.category,
                color=item.color,
                size=item.size,
                price=item.price,
                branch_name=item.branch_name,
            )
            for index, item in enumerate(products[:limit], start=1)
        ]
        state.shopping_stage = "presented"

    async def save(self, state: ConversationState) -> ConversationState:
        return await self._repository.save(state)

    @staticmethod
    def to_view(state: ConversationState) -> ConversationView:
        return ConversationView(
            conversation_id=state.conversation_id,
            cart_id=state.cart_id,
            messages=state.messages,
            active_agent=state.active_agent,
            current_intent=state.current_intent,
            shopping_stage=state.shopping_stage,
            created_at=state.created_at,
            updated_at=state.updated_at,
        )
