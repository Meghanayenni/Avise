"""What data the case holds, so that gaps can be computed rather than decorated.

"Transaction records were never requested" is a different and more actionable
statement than "no transaction records found".
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, model_validator

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import CoverageStatus, SourceType


class CaseDataCoverage(AviseModel):
    id: UUID
    case_id: UUID
    source_type: SourceType
    #: Null means the declaration covers the case rather than one entity.
    subject_entity_id: UUID | None = None
    period_from: UtcDatetime
    period_to: UtcDatetime
    status: CoverageStatus
    requested_at: UtcDatetime | None = None
    received_at: UtcDatetime | None = None
    note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def _period_runs_forward(self) -> CaseDataCoverage:
        if self.period_to <= self.period_from:
            raise ValueError("period_to must follow period_from")
        return self
