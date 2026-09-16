"""Where a claim came from, in a form that fits the source it came from.

Character offsets carry meaning for FIR narratives and surveillance notes. They
carry none for a CDR row, and inventing them there would make "open the source"
a lie for most of the corpus. So a locator is a discriminated union:

    text_span      document + character range   narrative text
    record_field   record + field name          one field of a tabular record
    record_row     record                       a whole tabular record

PHASE-0-DECISIONS A4. The same union applies to mentions and to edge provenance.
"""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel
from avise.domain.enums import LocatorKind


class _LocatorBase(AviseModel):
    """Shared behaviour: the discriminator is always serialised.

    `kind` carries a default, so Pydantic would treat it as unset and
    `model_dump(exclude_unset=True)` would drop it - leaving a locator that no
    longer says what kind it is. Marking it set at construction closes that hole
    the same way `edge_origin` is closed on edges.
    """

    @model_validator(mode="after")
    def _keep_discriminator_set(self) -> _LocatorBase:
        self.__pydantic_fields_set__.add("kind")
        return self


class TextSpan(_LocatorBase):
    """A character range in a document's text."""

    kind: Literal[LocatorKind.TEXT_SPAN] = LocatorKind.TEXT_SPAN
    document_id: UUID
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)

    @model_validator(mode="after")
    def _end_follows_start(self) -> TextSpan:
        if self.char_end <= self.char_start:
            raise ValueError("char_end must follow char_start")
        return self

    @property
    def length(self) -> int:
        return self.char_end - self.char_start


class RecordField(_LocatorBase):
    """One field of one tabular record - a CDR column, a transaction amount."""

    kind: Literal[LocatorKind.RECORD_FIELD] = LocatorKind.RECORD_FIELD
    record_id: UUID
    field_name: str = Field(min_length=1, max_length=120)


class RecordRow(_LocatorBase):
    """A whole tabular record, when no single field is the source."""

    kind: Literal[LocatorKind.RECORD_ROW] = LocatorKind.RECORD_ROW
    record_id: UUID


SourceLocator = Annotated[
    TextSpan | RecordField | RecordRow, Field(discriminator="kind")
]
