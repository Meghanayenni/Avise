"""Identity hypotheses and the decisions that resolve them.

Nothing here merges anything. A confirmed merge is an overlay written from a
decision; the underlying entities and their mentions stay separate for good.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import IdentityState

#: A decision moves a hypothesis out of PROPOSED, or reverses an earlier one.
TERMINAL_STATES = {
    IdentityState.CONFIRMED,
    IdentityState.REJECTED,
    IdentityState.NEEDS_EVIDENCE,
    IdentityState.DEFERRED,
}


class IdentityFeature(AviseModel):
    """One scored reason, in the investigator's language rather than a coefficient."""

    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=300)
    value: float
    role: str = Field(pattern=r"^(supporting|contradicting|not_known)$")


class IdentityHypothesis(AviseModel):
    id: UUID
    case_id: UUID
    left_entity_id: UUID
    right_entity_id: UUID
    #: Stays PROPOSED indefinitely. No timeout resolves it.
    state: IdentityState = IdentityState.PROPOSED
    score: float = Field(ge=0.0, le=1.0)
    #: The full feature vector is preserved, so the card can show its reasons.
    features: list[IdentityFeature] = Field(default_factory=list)
    blocking_key: str | None = None
    created_at: UtcDatetime

    @model_validator(mode="after")
    def _distinct_entities(self) -> IdentityHypothesis:
        if self.left_entity_id == self.right_entity_id:
            raise ValueError("a hypothesis needs two distinct entities")
        return self


class IdentityDecision(AviseModel):
    """A human's recorded decision. No merge exists without one."""

    id: UUID
    case_id: UUID
    hypothesis_id: UUID
    from_state: IdentityState
    to_state: IdentityState
    decided_by: UUID
    decided_at: UtcDatetime
    #: The evidence exactly as shown at decision time, not as it stands now.
    evidence_snapshot: dict[str, Any]
    rationale_text: str | None = Field(default=None, max_length=2000)
    superseded_by: UUID | None = None

    @model_validator(mode="after")
    def _state_actually_changes(self) -> IdentityDecision:
        if self.from_state == self.to_state:
            raise ValueError("a decision must change the state")
        if self.to_state not in TERMINAL_STATES:
            raise ValueError("a decision moves a hypothesis out of PROPOSED")
        return self
