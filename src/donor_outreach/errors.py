class DomainError(Exception):
   """Base class for all known and expected application errors."""
   code: str = "domain_error"
   status: int = 500
   def __init__(self, detail: str | None = None):
        super().__init__(detail or self.code)
        self.detail = detail

class NotFoundError(DomainError):
    """Raised when a requested resource (campaign, message) doesn't exist."""

    code = "not_found"
    status = 404


class ValidationFailedError(DomainError):
    """Raised for domain-level validation failures that aren't caught by Pydantic."""

    code = "validation_failed"
    status = 422


class ConflictError(DomainError):
    """Raised when a request conflicts with the current state of a resource."""

    code = "conflict"
    status = 409


class UpstreamServiceError(DomainError):
    """Raised when a Comprehend or Translate call fails."""

    code = "upstream_service_error"
    status = 502