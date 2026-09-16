"""Investigator notes. Never affects analytics: a note about a node is a note."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime


class Annotation(AviseModel):
    id: UUID
    case_id: UUID
    #: Null target means a free-standing note on the board.
    target_type: str | None = Field(default=None, max_length=40)
    target_id: UUID | None = None
    body: str = Field(min_length=1, max_length=5000)
    author_id: UUID
    created_at: UtcDatetime
    edited_at: UtcDatetime | None = None
    pinned: bool = False
