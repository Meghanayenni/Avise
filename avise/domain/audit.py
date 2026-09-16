"""The audit contract: the complete event enum and the row shape.

The enum is defined in full in Phase 0 so later phases add emission sites rather
than migrations. Phase 0 emits only the subset it can trigger.

The audit log is the investigative record. Operational logs are not - see
avise.core.logging.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime


class AuditAction(StrEnum):
    """PHASE-0-DECISIONS A6, in full."""

    AUTH_REGISTER = "auth.register"
    AUTH_ACTIVATE = "auth.activate"
    AUTH_LOGIN = "auth.login"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_LOCKOUT = "auth.lockout"
    AUTH_LOGOUT = "auth.logout"

    ACCOUNT_CAPABILITY_GRANTED = "account.capability_granted"
    ACCOUNT_CAPABILITY_REVOKED = "account.capability_revoked"
    ACCOUNT_SUSPENDED = "account.suspended"
    ACCOUNT_REACTIVATED = "account.reactivated"

    CASE_CREATED = "case.created"
    CASE_OPENED = "case.opened"
    CASE_CLOSED = "case.closed"
    CASE_REOPENED = "case.reopened"

    MEMBERSHIP_GRANTED = "membership.granted"
    MEMBERSHIP_REVOKED = "membership.revoked"
    MEMBERSHIP_LEAD_TRANSFERRED = "membership.lead_transferred"

    INVITATION_SENT = "invitation.sent"
    INVITATION_ACCEPTED = "invitation.accepted"
    INVITATION_DECLINED = "invitation.declined"
    INVITATION_REVOKED = "invitation.revoked"
    INVITATION_EXPIRED = "invitation.expired"

    IDENTITY_DECIDED = "identity.decided"
    IDENTITY_REVERSED = "identity.reversed"

    ANNOTATION_CREATED = "annotation.created"
    ANNOTATION_EDITED = "annotation.edited"
    ANNOTATION_DELETED = "annotation.deleted"

    ASSERTION_CREATED = "assertion.created"
    ASSERTION_EDITED = "assertion.edited"
    ASSERTION_REVOKED = "assertion.revoked"

    RESTRICTED_VIEWED = "restricted.viewed"

    REPORT_GENERATED = "report.generated"
    REPORT_EXPORTED = "report.exported"


#: The actions Phase 0 can trigger. Later phases add emission sites, not values.
PHASE_0_ACTIONS = frozenset(
    {
        AuditAction.AUTH_REGISTER,
        AuditAction.AUTH_ACTIVATE,
        AuditAction.AUTH_LOGIN,
        AuditAction.AUTH_LOGIN_FAILED,
        AuditAction.AUTH_LOCKOUT,
        AuditAction.AUTH_LOGOUT,
        AuditAction.ACCOUNT_CAPABILITY_GRANTED,
        AuditAction.ACCOUNT_CAPABILITY_REVOKED,
        AuditAction.CASE_CREATED,
        AuditAction.CASE_OPENED,
        AuditAction.CASE_CLOSED,
        AuditAction.MEMBERSHIP_GRANTED,
        AuditAction.MEMBERSHIP_REVOKED,
    }
)


class AuditEntry(AviseModel):
    """One append-only, hash-chained row. `row_hash = H(prev_hash || payload)`."""

    id: UUID
    actor_user_id: UUID | None = None
    action: AuditAction
    case_id: UUID | None = None
    target_type: str | None = Field(default=None, max_length=40)
    target_id: UUID | None = None
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    at: UtcDatetime
    ip: str | None = Field(default=None, max_length=45)
    prev_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    row_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
