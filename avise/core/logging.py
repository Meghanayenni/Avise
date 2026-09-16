"""Operational logging.

Logs are operational and discardable: they exist to debug a running process and
may be rotated away at any time. The hash-chained `audit_log` table is the
investigative record. They are not the same thing and must not be conflated -
nothing logged here is evidence, and nothing evidential may live only here.

Never logged: passwords, session tokens or their hashes, Cookie and
Authorization headers, entity names, case content, record payloads.

Logged: request id, method, route TEMPLATE (never a populated path, which would
carry case and entity identifiers), status, duration, user id, error class.

Redaction is structural: the formatter emits a fixed set of keys and silently
drops every other attribute, so a caller cannot widen a log line by passing
extra fields.
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")

#: Third-party loggers that emit fully populated URLs or SQL at INFO. Their
#: messages are outside our formatter's control - the formatter fixes the keys,
#: not the message text - so they are held at WARNING.
QUIET_LOGGERS = (
    "httpx",
    "httpcore",
    "urllib3",
    "python_multipart",
    "multipart",
    "sqlalchemy.engine",
    "alembic",
    "asyncio",
)

#: The only record attributes a log line may carry beyond the fixed envelope.
SAFE_EXTRA_KEYS = frozenset(
    {"event", "method", "route", "status", "duration_ms", "error_class", "job_id"}
)


class JsonFormatter(logging.Formatter):
    """Formats records as one JSON object per line, dropping unlisted attributes."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
        }
        for key in SAFE_EXTRA_KEYS:
            if key in record.__dict__:
                payload[key] = record.__dict__[key]
        if record.exc_info and record.exc_info[0] is not None:
            # The class only. A traceback can echo request data into the log.
            payload["error_class"] = record.exc_info[0].__name__
        return json.dumps(payload, separators=(",", ":"), default=str)


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter and silence uvicorn's access log.

    Uvicorn's access log prints fully populated paths, which for AVISE means case
    and entity UUIDs on every line. Our own middleware logs the route template
    instead.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    access = logging.getLogger("uvicorn.access")
    access.handlers = []
    access.propagate = False
    access.disabled = True

    for name in ("uvicorn", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers = [handler]
        logger.propagate = False

    quiet_third_party_loggers()


def quiet_third_party_loggers() -> None:
    """Hold libraries that log populated URLs or SQL at WARNING.

    `httpx` logs the request URL at INFO, which in AVISE means a case UUID on
    every line. Our formatter cannot redact another library's message text, so
    the level is the control.
    """
    for name in QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def new_request_id() -> str:
    """A correlation id, returned to the client in the error envelope."""
    return uuid.uuid4().hex
