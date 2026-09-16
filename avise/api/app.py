"""The FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from avise.api.middleware import RequestContextMiddleware
from avise.api.routes import health
from avise.core.config import get_settings
from avise.core.errors import register_error_handlers
from avise.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="AVISE",
        version="0.1.0",
        description="Case-centric investigation workspace.",
    )

    # One origin, credentials allowed, because the session travels as a cookie.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    return app


app = create_app()
