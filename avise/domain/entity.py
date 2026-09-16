"""Entities: the nodes. Nothing about a person is ever clustered automatically."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import EntityType

#: Human-facing reference, unique per (case_id, entity_type) and stable once
#: assigned: P-0041, CDR-0231. Rendered in mono type; never a database key.
DISPLAY_REF_PATTERN = r"^[A-Z]{1,4}-[0-9]{4}$"


class EntityAttribute(AviseModel):
    """One recorded attribute, carrying the mention it came from."""

    name: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=500)
    source_mention_id: UUID | None = None


class Entity(AviseModel):
    id: UUID
    case_id: UUID
    entity_type: EntityType
    canonical_form: str = Field(min_length=1, max_length=500)
    display_ref: str = Field(pattern=DISPLAY_REF_PATTERN)
    #: Informants, protected witnesses, minors. Column now, gating UI in Phase 5.
    restricted: bool = False
    created_from_mention_id: UUID | None = None
    attributes: list[EntityAttribute] = Field(default_factory=list)
    first_seen_ts: UtcDatetime | None = None
    last_seen_ts: UtcDatetime | None = None
    created_at: UtcDatetime
