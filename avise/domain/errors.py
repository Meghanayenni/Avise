"""The domain exception hierarchy.

These live in `domain` because `core` imports `domain` and never the reverse.
`core.errors` translates them into HTTP; nothing here knows what HTTP is.
"""

from __future__ import annotations

from typing import Any


class AviseError(Exception):
    """Base for every expected AVISE failure."""

    code: str = "internal_error"
    http_status: int = 500
    default_message: str = "The request could not be completed."

    def __init__(
        self, message: str | None = None, *, details: dict[str, Any] | None = None
    ) -> None:
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


class InvalidInput(AviseError):
    code = "invalid_input"
    http_status = 422
    default_message = "The request was not valid."


class AuthenticationRequired(AviseError):
    code = "authentication_required"
    http_status = 401
    default_message = "Sign in to continue."


class AccountNotActive(AviseError):
    """A pending, suspended or deactivated account. Deliberately indistinguishable to the client."""

    code = "authentication_required"
    http_status = 401
    default_message = "Sign in to continue."


class PermissionDenied(AviseError):
    """Reached only when membership is already established - a lead-only action."""

    code = "permission_denied"
    http_status = 403
    default_message = "This action is available to the case lead."


class NotFound(AviseError):
    """Also the answer for a case the user is not a member of. Existence is sensitive."""

    code = "not_found"
    http_status = 404
    default_message = "Not found."


class Conflict(AviseError):
    code = "conflict"
    http_status = 409
    default_message = "That conflicts with the current state."


class RateLimited(AviseError):
    code = "rate_limited"
    http_status = 429
    default_message = "Too many attempts. Try again shortly."


class CaseScopeError(AviseError):
    """A programming error: case content was queried without a case_id."""

    code = "case_scope_error"
    http_status = 500
    default_message = "The request could not be completed."


class UnscopedQueryError(CaseScopeError):
    """Raised by the session guard when a case-scoped table is queried unscoped."""
