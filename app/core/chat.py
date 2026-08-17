"""FastAPI routing for the Single Agent chat endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agent.state import ConversationState
from app.core.container import AppContainer, get_container

router = APIRouter(tags=["chat"])

# In-memory session store since V1 state is requested to be structured and persistent,
# but we avoid a real DB for now per "Don't introduce speculative V2 infrastructure".
_SESSIONS: dict[str, ConversationState] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    state: ConversationState


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

    # Load or create session state
    if request.session_id not in _SESSIONS:
        _SESSIONS[request.session_id] = ConversationState(session_id=request.session_id)
        
    state = _SESSIONS[request.session_id]
    context = container.store_context.get_context()

    # Pass the message to the Single Agent
    reply = await container.agent.process_message(request.message, state, context)

    return ChatResponse(reply=reply, state=state)
