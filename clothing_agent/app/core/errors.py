"""Stable application errors returned by the agent API."""

from __future__ import annotations

from typing import Any


class AgentError(Exception):
    """Base exception carrying a stable API-safe error contract."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "AGENT_ERROR",
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AgentNotFoundError(AgentError):
    """Raised when a requested conversation or resource does not exist."""

    def __init__(self, message: str, *, code: str = "NOT_FOUND") -> None:
        super().__init__(message, code=code, status_code=404)


class DependencyUnavailableError(AgentError):
    """Raised when the clothing application or LLM cannot be reached."""

    def __init__(self, message: str, *, code: str = "DEPENDENCY_UNAVAILABLE") -> None:
        super().__init__(message, code=code, status_code=503)


class InvalidAgentRequestError(AgentError):
    """Raised when an agent action lacks a required product or cart reference."""

    def __init__(self, message: str, *, code: str = "INVALID_AGENT_REQUEST") -> None:
        super().__init__(message, code=code, status_code=422)
