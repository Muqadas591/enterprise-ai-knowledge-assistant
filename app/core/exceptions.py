class ApplicationError(Exception):
    """Base exception for application-level errors."""


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource does not exist."""


class UnauthorizedError(ApplicationError):
    """Raised when a user is not authorized."""


class InvalidFileError(ApplicationError):
    """Raised when an uploaded file is invalid."""
