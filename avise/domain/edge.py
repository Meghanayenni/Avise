"""Edges carry interpretation. Attribution lives on edge_provenance.

PHASE-0-DECISIONS A3: what the system concluded is here; where it came from is
there. `supporting_record_ids` is a derived view over provenance, never a column.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import EdgeClass, EdgeOrigin, EdgeType

IDENTITY_EDGE_TYPES = {EdgeType.SAME_AS}


class Edge(AviseModel):
    id: UUID
    case_id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    edge_class: EdgeClass
    edge_type: EdgeType
    #: Required, with no default. An edge that cannot say where it came from
    #: does not enter the graph.
    edge_origin: EdgeOrigin
    confidence: float = Field(ge=0.0, le=1.0)
    #: Why this confidence - shown to the investigator as reasons, not a number.
    confidence_basis: list[str] = Field(default_factory=list)
    first_seen_ts: UtcDatetime | None = None
    last_seen_ts: UtcDatetime | None = None
    #: Attached by the rule that produced the edge, not typed per instance.
    alternative_explanations: list[str] = Field(default_factory=list)
    inference_rule_id: str | None = None
    base_rate_context: dict[str, Any] | None = None
    created_at: UtcDatetime

    @model_validator(mode="after")
    def _inference_states_its_rule(self) -> Edge:
        if self.edge_origin is EdgeOrigin.SYSTEM_INFERRED and not self.inference_rule_id:
            raise ValueError("a system_inferred edge must name its inference_rule_id")
        if self.edge_origin is not EdgeOrigin.SYSTEM_INFERRED and self.inference_rule_id:
            raise ValueError("inference_rule_id belongs only to a system_inferred edge")
        return self

    @model_validator(mode="after")
    def _class_matches_type(self) -> Edge:
        identity_type = self.edge_type in IDENTITY_EDGE_TYPES
        if identity_type and self.edge_class is not EdgeClass.IDENTITY:
            raise ValueError(f"{self.edge_type} is an IDENTITY edge")
        if not identity_type and self.edge_class is EdgeClass.IDENTITY:
            raise ValueError(f"{self.edge_type} is not an IDENTITY edge")
        return self

    @model_validator(mode="after")
    def _no_self_edge(self) -> Edge:
        if self.source_entity_id == self.target_entity_id:
            raise ValueError("an edge cannot join an entity to itself")
        return self
