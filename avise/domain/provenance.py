"""Attribution: where an edge came from.

An edge may have many provenance rows and cannot persist without at least one
supporting row - invariant 2, second clause. Supporting and contradicting record
ids are derived here by filtering on role; they are never stored as columns,
because two places holding the same fact is how they drift apart.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.edge import Edge
from avise.domain.enums import ExtractionMethod, ProvenanceRole
from avise.domain.locator import RecordField, RecordRow, SourceLocator, TextSpan


class EdgeProvenance(AviseModel):
    id: UUID
    edge_id: UUID
    document_id: UUID | None = None
    record_id: UUID | None = None
    mention_id: UUID | None = None
    locator: SourceLocator
    role: ProvenanceRole
    #: Per row, not per edge: one edge may be supported by a regex match and a
    #: spaCy match, each with its own method.
    extraction_method: ExtractionMethod
    created_at: UtcDatetime

    @model_validator(mode="after")
    def _locator_matches_source(self) -> EdgeProvenance:
        if isinstance(self.locator, TextSpan) and self.document_id is None:
            raise ValueError("a text_span provenance row requires document_id")
        if isinstance(self.locator, (RecordField, RecordRow)) and self.record_id is None:
            raise ValueError("a record provenance row requires record_id")
        return self


class ProvenancedEdge(AviseModel):
    """An edge together with its provenance - the only form that may be written."""

    edge: Edge
    provenance: list[EdgeProvenance] = Field(min_length=1)

    @model_validator(mode="after")
    def _has_supporting_provenance(self) -> ProvenancedEdge:
        if not any(row.role is ProvenanceRole.SUPPORTING for row in self.provenance):
            raise ValueError("an edge requires at least one supporting provenance row")
        if any(row.edge_id != self.edge.id for row in self.provenance):
            raise ValueError("provenance rows must reference their own edge")
        return self

    @property
    def supporting(self) -> list[EdgeProvenance]:
        return [row for row in self.provenance if row.role is ProvenanceRole.SUPPORTING]

    @property
    def contradicting(self) -> list[EdgeProvenance]:
        return [row for row in self.provenance if row.role is ProvenanceRole.CONTRADICTING]

    @property
    def supporting_record_ids(self) -> list[UUID]:
        """Derived view. Report section 7 - not a column."""
        return [row.record_id for row in self.supporting if row.record_id is not None]

    @property
    def contradicting_record_ids(self) -> list[UUID]:
        """Derived view. Evidence against is part of the contract, not an add-on."""
        return [row.record_id for row in self.contradicting if row.record_id is not None]
