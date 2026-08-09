import pytest
from app.core.chat import ChatRequest
from pydantic import ValidationError


def test_chat_contract_creates_conversation_from_first_real_message():
    request = ChatRequest(message="I want a casual summer shirt")
    assert request.conversation_id is None
    assert request.message == "I want a casual summer shirt"


def test_chat_contract_rejects_empty_bootstrap_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="")
