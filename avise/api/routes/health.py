"""Liveness. The only route in AVISE that touches no case and writes no audit row."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from avise.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok", service="avise", environment=get_settings().environment
    )
