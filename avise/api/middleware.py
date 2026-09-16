"""Request context: correlation id, timing, and the one access log line we keep."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from avise.core.logging import new_request_id, request_id_var

logger = logging.getLogger("avise.request")


def route_template(request: Request) -> str:
    """The route template, never the populated path.

    `/api/cases/{case_id}` is safe to log. `/api/cases/3f2b.../` identifies a case,
    and a log file is not the audit trail.
    """
    route = request.scope.get("route")
    template = getattr(route, "path_format", None)
    return str(template) if template else "unmatched"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        token = request_id_var.set(new_request_id())
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "request",
            extra={
                "event": "request",
                "method": request.method,
                "route": route_template(request),
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        response.headers["X-Request-Id"] = request_id_var.get()
        request_id_var.reset(token)
        return response
