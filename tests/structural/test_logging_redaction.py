"""A request carrying a session token and a case id must leave neither in the logs.

Redaction is structural - the formatter emits a fixed key set - so these tests
drive the real formatter and the real middleware rather than inspecting strings
we hand it.
"""

from __future__ import annotations

import io
import json
import logging
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from avise.api.middleware import RequestContextMiddleware
from avise.core.errors import register_error_handlers
from avise.core.logging import (
    JsonFormatter,
    configure_logging,
    quiet_third_party_loggers,
)

CASE_ID = "8f14e45f-ea9b-4f2c-9d2a-1b3c4d5e6f70"
SESSION_TOKEN = "s3ss10n-t0ken-must-never-be-logged"
PASSWORD = "correct-horse-battery"


@pytest.fixture
def log_stream() -> Iterator[io.StringIO]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    quiet_third_party_loggers()
    root = logging.getLogger()
    previous_handlers, previous_level = root.handlers, root.level
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    try:
        yield stream
    finally:
        root.handlers, root.level = previous_handlers, previous_level


@pytest.fixture
def probe_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    @app.get("/api/cases/{case_id}")
    def read_case(case_id: str) -> dict[str, str]:
        return {"case_id": case_id}

    return TestClient(app)


def test_request_log_omits_token_case_id_and_headers(
    probe_client: TestClient, log_stream: io.StringIO
) -> None:
    probe_client.cookies.set("avise_session", SESSION_TOKEN)
    response = probe_client.get(
        f"/api/cases/{CASE_ID}",
        headers={"Authorization": "Bearer secret-value", "X-Password": PASSWORD},
    )
    assert response.status_code == 200

    logged = log_stream.getvalue()
    assert logged.strip(), "the request produced no log line at all"
    for secret in (SESSION_TOKEN, CASE_ID, PASSWORD, "Bearer", "secret-value"):
        assert secret not in logged, f"{secret!r} reached the log"


def test_request_log_records_the_route_template(
    probe_client: TestClient, log_stream: io.StringIO
) -> None:
    probe_client.get(f"/api/cases/{CASE_ID}")
    line = json.loads(log_stream.getvalue().strip().splitlines()[-1])
    assert line["route"] == "/api/cases/{case_id}"
    assert line["method"] == "GET"
    assert line["status"] == 200
    assert line["request_id"] != "-"
    assert isinstance(line["duration_ms"], (int, float))


def test_unmatched_path_is_not_logged_verbatim(
    probe_client: TestClient, log_stream: io.StringIO
) -> None:
    probe_client.get(f"/api/cases/{CASE_ID}/entities/secret-entity")
    logged = log_stream.getvalue()
    assert "secret-entity" not in logged
    assert '"route":"unmatched"' in logged


def test_formatter_drops_unlisted_extras(log_stream: io.StringIO) -> None:
    logging.getLogger("avise.test").info(
        "probe", extra={"entity_name": "Deepak Rao", "payload": {"phone": "9840012345"}}
    )
    line = json.loads(log_stream.getvalue().strip())
    assert "entity_name" not in line
    assert "payload" not in line
    assert "9840012345" not in log_stream.getvalue()


def test_configure_logging_disables_uvicorn_access_log() -> None:
    root = logging.getLogger()
    previous_handlers, previous_level = root.handlers, root.level
    try:
        configure_logging("INFO")
        access = logging.getLogger("uvicorn.access")
        assert access.disabled
        assert access.handlers == []
        assert access.propagate is False
    finally:
        root.handlers, root.level = previous_handlers, previous_level
