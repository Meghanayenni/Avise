"""Access shapes: the account, the case, the membership, the invitation.

The credential identifies the person and nothing else. There is no case list, no
standing and no capability in the session, so membership is re-resolved from the
database on every request and revocation takes effect on the very next one.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import (
    AccountCapability,
    AccountStatus,
    CaseStatus,
    InvitationStatus,
    Standing,
)

#: Official email. A pattern rather than pydantic's EmailStr, which needs the
#: email-validator package - not on the approved dependency list. Accounts are
#: provisioned against a service id; the address is a contact detail.
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

#: CASE-YYYY-NNNN, unique system-wide. A case spans stations, so no station
#: appears here: station belongs on the FIR.
CASE_NUMBER_PATTERN = r"^CASE-[0-9]{4}-[0-9]{4}$"


class UserProfile(AviseModel):
    """Exactly what /api/auth/me returns. Nothing about cases or permissions."""

    id: UUID
    service_id: str = Field(min_length=1, max_length=40)
    full_name: str = Field(min_length=1, max_length=200)
    #: Descriptive only. SI, ASI, Inspector - confers nothing.
    designation: str = Field(min_length=1, max_length=80)
    status: AccountStatus


class UserAccount(AviseModel):
    """The server-side account. The password hash never leaves the database layer."""

    id: UUID
    service_id: str = Field(min_length=1, max_length=40)
    full_name: str = Field(min_length=1, max_length=200)
    designation: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=320)
    status: AccountStatus = AccountStatus.PENDING_VERIFICATION
    capabilities: list[AccountCapability] = Field(default_factory=list)
    created_by: UUID | None = None
    created_at: UtcDatetime
    last_login_at: UtcDatetime | None = None


class Case(AviseModel):
    id: UUID
    case_number: str = Field(pattern=CASE_NUMBER_PATTERN)
    title: str = Field(min_length=1, max_length=300)
    status: CaseStatus = CaseStatus.OPEN
    created_by: UUID
    opened_at: UtcDatetime
    closed_at: UtcDatetime | None = None


class CaseSummary(AviseModel):
    """A case as it appears on the personal dashboard, with the reader's standing."""

    id: UUID
    case_number: str = Field(pattern=CASE_NUMBER_PATTERN)
    title: str = Field(min_length=1, max_length=300)
    status: CaseStatus
    standing: Standing
    opened_at: UtcDatetime
    closed_at: UtcDatetime | None = None


class CaseMembership(AviseModel):
    """The grant. This list is the team; there is no separate team object."""

    id: UUID
    case_id: UUID
    user_id: UUID
    standing: Standing
    granted_by: UUID
    granted_at: UtcDatetime
    expires_at: UtcDatetime | None = None
    revoked_at: UtcDatetime | None = None
    revoke_reason: str | None = Field(default=None, max_length=500)


class CaseInvitation(AviseModel):
    """Names a specific account. Never a bearer code. Lifecycle logic is Phase 5."""

    id: UUID
    case_id: UUID
    invited_user_id: UUID
    invited_by: UUID
    standing: Standing = Standing.INVESTIGATOR
    status: InvitationStatus = InvitationStatus.SENT
    created_at: UtcDatetime
    expires_at: UtcDatetime
    responded_at: UtcDatetime | None = None
