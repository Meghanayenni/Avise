"""The evidence drawer contract.

One shape, served by one endpoint, opened from every "why?" in the application.
Six bespoke detail panels is how explainability decays into three good ones and
three that print a percentage.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel
from avise.domain.enums import ConfidenceBand, EdgeOrigin, EntityType, SourceType
from avise.domain.locator import SourceLocator


class EvidenceSubject(AviseModel):
    subject_type: str = Field(min_length=1, max_length=40)
    id: UUID
    label: str = Field(min_length=1, max_length=300)
    entity_type: EntityType | None = None


class EvidenceRef(AviseModel):
    """One pointer into a source, resolvable to a highlight."""

    label: str = Field(min_length=1, max_length=300)
    locator: SourceLocator
    source_type: SourceType
    document_id: UUID | None = None
    record_id: UUID | None = None
    occurred_at: str | None = None


class DerivationStep(AviseModel):
    order: int = Field(ge=1)
    statement: str = Field(min_length=1, max_length=500)
    rule_id: str | None = None


class Confidence(AviseModel):
    band: ConfidenceBand
    basis: list[str] = Field(default_factory=list)


class DrawerAction(AviseModel):
    key: str = Field(min_length=1, max_length=60)
    label: str = Field(min_length=1, max_length=80)
    enabled: bool = True


class EvidenceDrawer(AviseModel):
    """Report section 17. Every field is part of the contract, including the absences."""

    subject: EvidenceSubject
    #: From the controlled vocabulary. Never a free-text claim.
    claim: str = Field(min_length=1, max_length=500)
    origin: EdgeOrigin
    supporting: list[EvidenceRef] = Field(default_factory=list)
    contradicting: list[EvidenceRef] = Field(default_factory=list)
    #: What would help and is absent. Prevents absence reading as contradiction.
    unknown: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    derivation: list[DerivationStep] = Field(default_factory=list)
    confidence: Confidence
    actions: list[DrawerAction] = Field(default_factory=list)
