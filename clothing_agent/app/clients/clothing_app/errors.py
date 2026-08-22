"""Clothing-application client errors."""

from ...core.errors import DependencyUnavailableError


class ClothingAppUnavailableError(DependencyUnavailableError):
    """Raised when the clothing application cannot satisfy a request."""

    def __init__(self, message: str = "The clothing application is unavailable.") -> None:
        super().__init__(message, code="CLOTHING_APP_UNAVAILABLE")
