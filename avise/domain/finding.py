"""Findings: what was found, with its limits attached.

Separate from leads, in a separate table with a separate renderer, because a
finding and a question are different objects and collapsing them is how a
suggestion starts reading as a conclusion.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import ContentOrigin, FindingStatus
from avise.domain.evidence import Confidence, EvidenceRef


class Finding(AviseModel):
    id: UUID
    case_id: UUID
    #: Key into the controlled vocabulary - the claim is rendered, never typed.
    claim_key: str = Field(min_length=1, max_length=60)
    claim_values: dict[str, str] = Field(default_factory=dict)
    origin: ContentOrigin
    supporting: list[EvidenceRef] = Field(default_factory=list)
    contradicting: list[EvidenceRef] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    confidence: Confidence
    derived_from: list[UUID] = Field(default_factory=list)
    status: FindingStatus = FindingStatus.ACTIVE
    created_at: UtcDatetime
