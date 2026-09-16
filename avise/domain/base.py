"""The base model every domain contract inherits.

`extra="forbid"` is deliberate: an unknown field in a payload is a contract
mismatch, and silently dropping it is how a provenance field goes missing.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AviseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
