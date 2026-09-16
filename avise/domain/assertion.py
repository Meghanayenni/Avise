"""Investigator assertions: knowledge from outside the data, entering the graph.

The symmetry rule. The system states how it knows; so does the investigator. An
assertion without a stated basis is rejected here and again in the database, per
PHASE-0-DECISIONS A7.

Versions are kept by supersession, never by overwriting: an edit that changes the
claim writes a new row pointing at the old one, and the old row is revoked.
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime

#: The database CHECK enforces the same floor independently.
MINIMUM_BASIS_LENGTH = 10


class InvestigatorAssertion(AviseModel):
    id: UUID
    case_id: UUID
    assertion_kind: Literal["relationship", "entity"]
    #: The edge or entity definition this assertion places into the case.
    payload: dict[str, Any]
    #: "witness statement of complainant, 14 Mar." Not optional, ever.
    basis: str = Field(min_length=MINIMUM_BASIS_LENGTH, max_length=2000)
    author_id: UUID
    created_at: UtcDatetime
    #: Typo fixes that do not change the claim. Anything else supersedes.
    edited_at: UtcDatetime | None = None
    revoked_at: UtcDatetime | None = None
    revoked_by: UUID | None = None
    produced_edge_id: UUID | None = None
    produced_entity_id: UUID | None = None
    supersedes_id: UUID | None = None

    @model_validator(mode="after")
    def _basis_is_more_than_whitespace(self) -> InvestigatorAssertion:
        if len(self.basis.strip()) < MINIMUM_BASIS_LENGTH:
            raise ValueError(
                f"basis must state how this is known, at least {MINIMUM_BASIS_LENGTH} characters"
            )
        return self

    @model_validator(mode="after")
    def _revocation_names_who(self) -> InvestigatorAssertion:
        if (self.revoked_at is None) != (self.revoked_by is None):
            raise ValueError("a revocation records both when and by whom")
        return self

    @model_validator(mode="after")
    def _kind_matches_product(self) -> InvestigatorAssertion:
        if self.assertion_kind == "entity" and self.produced_edge_id is not None:
            raise ValueError("an entity assertion does not produce an edge")
        if self.assertion_kind == "relationship" and self.produced_entity_id is not None:
            raise ValueError("a relationship assertion does not produce an entity")
        return self
