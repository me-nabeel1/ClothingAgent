"""Conversation API and turn orchestration."""

from __future__ import annotations

import logging
from time import perf_counter
from uuid import UUID

from app.agents.registry import AgentRegistry
from app.agents.schemas import AgentRequest
from app.clients.clothing_app.schemas import CartView, ProductOption
from app.core.config import AgentConfig
from app.core.conversation import ConversationService
from app.core.routing import RouterService
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
audit = logging.getLogger("sales_audit")
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str | None = Field(default=None, max_length=1200)
    conversation_id: UUID | None = None


class ChatTurnResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    reply: str
    active_agent: str
    intent: str
    products: list[ProductOption] = Field(default_factory=list)
    cart: CartView | None = None
    suggested_actions: list[str] = Field(default_factory=list)


class OrchestratorService:
    def __init__(
        self,
        conversations: ConversationService,
        router_service: RouterService,
        agents: AgentRegistry,
        config: AgentConfig,
    ) -> None:
        self._conversations = conversations
        self._router = router_service
        self._agents = agents
        self._config = config

    async def handle_chat(self, request: ChatRequest) -> ChatTurnResponse:
        started = perf_counter()

        if not request.conversation_id:
            state = await self._conversations.create()
            audit.info(
                "conversation_started",
                extra={
                    "event": "conversation_started",
                    "conversation_id": str(state.conversation_id),
                },
            )
            if not request.message:
                await self._conversations.append_message(
                    state, role="assistant", content="Hi there! I am your personal shopping concierge. How can I help you today?"
                )
                state = await self._conversations.save(state)
                assistant_message = state.messages[-1]
                return ChatTurnResponse(
                    conversation_id=state.conversation_id,
                    message_id=assistant_message.message_id,
                    reply=assistant_message.content,
                    active_agent="sales",
                    intent="greeting",
                )
            conversation_id = state.conversation_id
        else:
            conversation_id = request.conversation_id
            state = await self._conversations.get(conversation_id)

        message = request.message or ""
        if not message.strip():
            if not state.messages:
                await self._conversations.append_message(
                    state, role="assistant", content="Hi there! I am your personal shopping concierge. How can I help you today?"
                )
                state = await self._conversations.save(state)
            
            assistant_message = state.messages[-1]
            return ChatTurnResponse(
                conversation_id=state.conversation_id,
                message_id=assistant_message.message_id,
                reply=assistant_message.content,
                active_agent="sales",
                intent="greeting",
            )



        audit.info(
            "turn_started",
            extra={
                "event": "turn_started",
                "conversation_id": str(conversation_id),
                "shopping_stage": state.shopping_stage,
                "clarification_count": state.clarification_count,
                "message_preview": message[:160],
            },
        )
        try:
            await self._conversations.append_message(state, role="user", content=message)
            route = await self._router.route(message, state)
            audit.info(
                "route_decided",
                extra={
                    "event": "route_decided",
                    "conversation_id": str(conversation_id),
                    "intent": route.intent.value,
                    "target_agent": route.target_agent.value,
                    "confidence": route.confidence,
                },
            )
            agent = self._agents.get(route.target_agent)
            result = await agent.handle(
                AgentRequest(message=message, context=state, route=route)
            )

            if result.products:
                self._conversations.set_displayed_products(
                    state,
                    result.products,
                    limit=self._config.displayed_product_limit,
                )
            for key, value in result.state_updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)

            state.active_agent = route.target_agent.value
            state.current_intent = route.intent.value
            await self._conversations.append_message(
                state, role="assistant", content=result.reply
            )
            state = await self._conversations.save(state)
            assistant_message = state.messages[-1]
            audit.info(
                "turn_completed",
                extra={
                    "event": "turn_completed",
                    "conversation_id": str(conversation_id),
                    "intent": state.current_intent,
                    "active_agent": state.active_agent,
                    "shopping_stage": state.shopping_stage,
                    "product_count": len(result.products),
                    "cart_item_count": len(result.cart.items) if result.cart else None,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            return ChatTurnResponse(
                conversation_id=state.conversation_id,
                message_id=assistant_message.message_id,
                reply=result.reply,
                active_agent=state.active_agent,
                intent=state.current_intent,
                products=result.products,
                cart=result.cart,
                suggested_actions=result.suggested_actions,
            )
        except Exception:
            logger.exception(
                "conversation_turn_failed",
                extra={
                    "event": "conversation_turn_failed",
                    "conversation_id": str(conversation_id),
                    "shopping_stage": state.shopping_stage,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            audit.error(
                "turn_failed",
                extra={
                    "event": "turn_failed",
                    "conversation_id": str(conversation_id),
                    "shopping_stage": state.shopping_stage,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            raise


def get_container():
    from app.core.container import get_container as resolve_container

    return resolve_container()


@router.post("", response_model=ChatTurnResponse)
async def chat_endpoint(
    body: ChatRequest,
    container=Depends(get_container),
) -> ChatTurnResponse:
    return await container.orchestrator.handle_chat(body)
