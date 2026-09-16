"""Leads: what question is open, and what would answer it.

A lead is always phrased as a question or a suggestion. A lead that reads as a
statement is a bug, asserted in the vocabulary test.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import LeadSource, LeadStatus


class Lead(AviseModel):
    id: UUID
    case_id: UUID
    question: str = Field(min_length=1, max_length=500)
    what_would_answer_it: list[str] = Field(default_factory=list)
    sources_to_consult: list[str] = Field(default_factory=list)
    why_it_matters_now: str | None = Field(default=None, max_length=500)
    source: LeadSource
    #: Structural impact, not confidence and not arrival order.
    priority: float = Field(ge=0.0, le=1.0)
    status: LeadStatus = LeadStatus.OPEN
    #: Not every lead comes from a finding; evidence gaps produce leads alone.
    linked_finding_id: UUID | None = None
    created_at: UtcDatetime
