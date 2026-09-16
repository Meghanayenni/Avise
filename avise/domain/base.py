"""The base model every domain contract inherits.

`extra="forbid"` is deliberate: an unknown field in a payload is a contract
mismatch, and silently dropping it is how a provenance field goes missing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict


class AviseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def _require_utc(value: datetime) -> datetime:
    """Timestamps are normalised to UTC at ingestion; a naive one is a bug upstream."""
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware and in UTC")
    return value


#: Every timestamp in the ontology. Report section 31: dates are UTC.
UtcDatetime = Annotated[datetime, AfterValidator(_require_utc)]
