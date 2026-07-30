class BODHException(Exception):
    """Base exception for application-level errors."""


class ResourceNotFoundError(BODHException):
    """Raised when a requested resource does not exist."""


class ResourceConflictError(BODHException):
    """Raised when an operation conflicts with existing data."""