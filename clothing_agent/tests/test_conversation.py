import pytest
from app.core.conversation import ConversationRepository, ConversationService


@pytest.mark.asyncio
async def test_conversation_starts_empty_without_session_or_greeting():
    service = ConversationService(ConversationRepository())
    state = await service.create()
    assert state.cart_id is None
    assert state.messages == []
    assert state.shopping_stage == "new"
    assert state.clarification_count == 0
