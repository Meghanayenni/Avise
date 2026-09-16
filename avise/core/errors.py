"""The HTTP error envelope and the handlers that translate domain errors into it.

Invalid input returns a structured envelope, never a 500 and never a bare string.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from avise.core.logging import request_id_var
from avise.domain.errors import AviseError

logger = logging.getLogger("avise.error")

_STATUS_CODES = {
    400: "invalid_input",
    401: "authentication_required",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "invalid_input",
    429: "rate_limited",
}


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict[str, Any] | None = None


class ErrorEnvelope(BaseModel):
    """The single error shape every AVISE endpoint returns."""

    error: ErrorBody


def build_envelope(
    code: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            request_id=request_id_var.get(),
            details=details,
        )
    )
    return envelope.model_dump()


def _sanitise_validation_errors(errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Keep location and reason; drop the offending value.

    Pydantic echoes the rejected input back in `input`, which for a login payload
    is the password.
    """
    fields = [
        {
            "location": [str(part) for part in error.get("loc", ())],
            "reason": str(error.get("msg", "")),
            "type": str(error.get("type", "")),
        }
        for error in errors
    ]
    return {"fields": fields}


def register_error_handlers(app: FastAPI) -> None:
    """Attach every handler. Called by the app factory, never at import time."""

    @app.exception_handler(AviseError)
    async def _domain_error(request: Request, exc: AviseError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=build_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=build_envelope(
                "invalid_input",
                "The request was not valid.",
                _sanitise_validation_errors(list(exc.errors())),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = _STATUS_CODES.get(exc.status_code, "error")
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(
            status_code=exc.status_code, content=build_envelope(code, detail)
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        # The message is generic: an exception string can carry case content.
        logger.exception("unhandled exception", extra={"event": "unhandled"})
        return JSONResponse(
            status_code=500,
            content=build_envelope(
                "internal_error", "The request could not be completed."
            ),
        )
