"""Persistent conversation-state storage for the V1 Agent prototype.

The store is file-backed to survive process restarts without introducing Redis or
another external service. It is intentionally designed as a swappable interface;
production multi-worker deployments can replace it with a database-backed store.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Protocol
from app.agent.state import ConversationState


class ConversationStateStore(Protocol):
    """Persistence contract for one conversation state."""
    def load(self, session_id: str) -> ConversationState | None: ...
    def save(self, state: ConversationState) -> None: ...


class FileConversationStateStore:
    """Store one Pydantic conversation state as an atomic JSON file."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._directory.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        safe = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in session_id)
        return self._directory / f"{safe}.json"

    def load(self, session_id: str) -> ConversationState | None:
        """Load a persisted session or return None when it does not exist."""
        path = self._path(session_id)
        if not path.exists():
            return None
        try:
            return ConversationState.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save(self, state: ConversationState) -> None:
        """Persist state atomically enough for the single-process prototype."""
        path = self._path(str(state.session_id))
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            state.model_dump_json(exclude_defaults=False),
            encoding="utf-8",
        )
        temporary.replace(path)
