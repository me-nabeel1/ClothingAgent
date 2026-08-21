"""Tests for persistent Agent session state."""
from pathlib import Path
from uuid import UUID
from clothing_agent.app.agent.state import ConversationState
from clothing_agent.app.core.state_store import FileConversationStateStore


def test_file_state_store_round_trip(tmp_path: Path) -> None:
    session_id = UUID("00000000-0000-0000-0000-000000000001")
    store = FileConversationStateStore(tmp_path / "sessions")
    state = ConversationState(session_id=session_id)
    state.preferences.preferred_colors = ["black"]
    store.save(state)

    loaded = store.load(str(session_id))
    assert loaded is not None
    assert loaded.session_id == session_id
    assert loaded.preferences.preferred_colors == ["black"]
