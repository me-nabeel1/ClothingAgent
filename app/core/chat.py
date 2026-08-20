"""FastAPI routing for the Single Agent chat and session management endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from clothing_agent.app.agent.state import ConversationState
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
            state.reset_current_search()
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
    state = get_or_create_session(request.session_id)
    return ChatResponse(reply="Fitzy Phase 1 foundation established.", state=state)


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

