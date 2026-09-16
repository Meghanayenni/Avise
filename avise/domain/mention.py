"""A mention: one surface form of one thing, at one place in one source."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import ExtractionMethod, MentionType
from avise.domain.locator import RecordField, RecordRow, SourceLocator, TextSpan


class Mention(AviseModel):
    """Extracted text or field, with the locator that points back at its source."""

    id: UUID
    case_id: UUID
    document_id: UUID | None = None
    record_id: UUID | None = None
    locator: SourceLocator
    surface_text: str = Field(min_length=1, max_length=500)
    mention_type: MentionType
    extraction_method: ExtractionMethod
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: UtcDatetime

    @model_validator(mode="after")
    def _locator_matches_source(self) -> Mention:
        """The locator and the source columns cannot disagree about the source."""
        if isinstance(self.locator, TextSpan):
            if self.document_id is None:
                raise ValueError("a text_span mention requires document_id")
            if self.document_id != self.locator.document_id:
                raise ValueError("document_id does not match the locator's document")
        if isinstance(self.locator, (RecordField, RecordRow)):
            if self.record_id is None:
                raise ValueError("a record locator requires record_id")
            if self.record_id != self.locator.record_id:
                raise ValueError("record_id does not match the locator's record")
        return self
