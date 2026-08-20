"""Errors for the Agent's commerce-API integration boundary."""

from __future__ import annotations


class CommerceClientError(RuntimeError):
    """Base error raised when a commerce API operation cannot be completed."""


class CommerceTransportError(CommerceClientError):
    """Raised when the configured commerce API cannot be reached."""


class CommerceHTTPError(CommerceClientError):
    """Raised when the commerce API returns an unsuccessful HTTP response."""

    def __init__(self, status_code: int, message: str, *, response_body: object | None = None) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"Commerce API returned HTTP {status_code}: {message}")


class CommerceValidationError(CommerceClientError):
    """Raised when a semantic Agent request cannot be mapped safely to the API."""
