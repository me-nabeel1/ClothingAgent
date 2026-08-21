"""Stable domain errors returned by the clothing application APIs."""


class AppError(Exception):
    """Base error with a public code, message, and HTTP status."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppError):
    """Raised when a requested application resource does not exist."""

    def __init__(self, message: str, *, code: str = "NOT_FOUND") -> None:
        super().__init__(message, code=code, status_code=404)


class ConflictError(AppError):
    """Raised when current stock or cart state prevents an operation."""

    def __init__(self, message: str, *, code: str = "CONFLICT") -> None:
        super().__init__(message, code=code, status_code=409)
