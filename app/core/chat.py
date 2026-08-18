"""FastAPI routing for the Single Agent chat and session management endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agent.state import ConversationState
from app.core.container import AppContainer, get_container

router = APIRouter(tags=["chat"])

# In-memory session store for structured session management.
_SESSIONS: dict[str, ConversationState] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    reset_session: Optional[bool] = False
    new_session: Optional[bool] = False
    reset: Optional[bool] = False


class ChatResponse(BaseModel):
    reply: str
    state: ConversationState


class SessionResetRequest(BaseModel):
    session_id: str
    keep_cart: bool = True


class SessionResetResponse(BaseModel):
    session_id: str
    status: str = "reset_successful"
    state: ConversationState


def get_or_create_session(session_id: str, reset: bool = False, keep_cart: bool = True) -> ConversationState:
    """Retrieve or initialize a ConversationState for a session, preserving cart items across new sessions."""
    clean_id = session_id.strip() if session_id and session_id.strip() else "default_session"
    if clean_id in _SESSIONS:
        state = _SESSIONS[clean_id]
        if reset:
            state.reset(keep_cart=keep_cart)
        return state
    
    new_state = ConversationState(session_id=clean_id)
    _SESSIONS[clean_id] = new_state
    return new_state


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    container: AppContainer = Depends(get_container),
) -> ChatResponse:
    """Process a single chat message using the unified AI agent."""
    
    if not container.store_context.is_loaded:
        try:
            await container.store_context.load_context()
        except Exception as e:
            raise HTTPException(503, f"Unable to load store context from backend: {e}")

    from app.agent.utils import is_greeting_or_reset_message

    should_reset = bool(request.reset_session or request.new_session or request.reset or is_greeting_or_reset_message(request.message))
    # Starting a new chat session retains active cart items while flushing all other preferences, history, and card holders
    state = get_or_create_session(request.session_id, reset=should_reset, keep_cart=True)
    context = container.store_context.get_context()

    # Pass the message to the Single Agent
    reply = await container.agent.process_message(request.message, state, context)

    return ChatResponse(reply=reply, state=state)


@router.post("/session/reset", response_model=SessionResetResponse)
@router.post("/session/new", response_model=SessionResetResponse)
async def reset_session_endpoint(
    request: SessionResetRequest,
) -> SessionResetResponse:
    """Flush chat history and preferences for the session while preserving active cart items if keep_cart is True."""
    state = get_or_create_session(request.session_id, reset=True, keep_cart=request.keep_cart)
    return SessionResetResponse(session_id=state.session_id, state=state)


@router.delete("/session/{session_id}", response_model=SessionResetResponse)
async def delete_session_endpoint(
    session_id: str,
) -> SessionResetResponse:
    """Delete session state and flush cart when explicitly requested."""
    state = get_or_create_session(session_id, reset=True, keep_cart=False)
    return SessionResetResponse(session_id=session_id, state=state)
