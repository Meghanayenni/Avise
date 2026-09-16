"""Background work. The table ships in Phase 0; the worker loop is Phase 1."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from avise.domain.base import AviseModel, UtcDatetime
from avise.domain.enums import JobKind, JobStatus


class Job(AviseModel):
    id: UUID
    case_id: UUID
    kind: JobKind
    status: JobStatus = JobStatus.QUEUED
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    error: str | None = Field(default=None, max_length=2000)
    created_at: UtcDatetime
    started_at: UtcDatetime | None = None
    finished_at: UtcDatetime | None = None
