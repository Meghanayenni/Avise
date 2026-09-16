"""Invalid input returns a structured envelope, never a 500 and never a bare string."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from avise.core.errors import register_error_handlers
from avise.domain.errors import Conflict, NotFound, PermissionDenied, RateLimited


@pytest.fixture
def probe_client() -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/missing")
    def missing() -> None:
        raise NotFound("Not found.")

    @app.get("/lead-only")
    def lead_only() -> None:
        raise PermissionDenied()

    @app.get("/conflict")
    def conflict() -> None:
        raise Conflict()

    @app.get("/slow-down")
    def slow_down() -> None:
        raise RateLimited()

    @app.get("/crash")
    def crash() -> None:
        raise RuntimeError("case CASE-2026-0001 belongs to Deepak Rao")

    @app.get("/typed/{number}")
    def typed(number: int) -> dict[str, int]:
        return {"number": number}

    @app.post("/login")
    def login(payload: dict[str, str]) -> dict[str, str]:
        return payload

    return TestClient(app, raise_server_exceptions=False)


def assert_envelope(body: dict[str, object], code: str) -> None:
    assert set(body) == {"error"}
    error = body["error"]
    assert isinstance(error, dict)
    assert set(error) == {"code", "message", "request_id", "details"}
    assert error["code"] == code
    assert isinstance(error["message"], str) and error["message"]


@pytest.mark.parametrize(
    ("path", "status", "code"),
    [
        ("/missing", 404, "not_found"),
        ("/lead-only", 403, "permission_denied"),
        ("/conflict", 409, "conflict"),
        ("/slow-down", 429, "rate_limited"),
    ],
)
def test_domain_errors_become_envelopes(
    probe_client: TestClient, path: str, status: int, code: str
) -> None:
    response = probe_client.get(path)
    assert response.status_code == status
    assert_envelope(response.json(), code)


def test_unhandled_exception_is_a_generic_envelope(probe_client: TestClient) -> None:
    response = probe_client.get("/crash")
    assert response.status_code == 500
    assert_envelope(response.json(), "internal_error")
    # The exception text named a case and a person; neither may reach the client.
    assert "Deepak" not in response.text
    assert "CASE-2026-0001" not in response.text


def test_validation_error_reports_location_but_not_value(
    probe_client: TestClient,
) -> None:
    response = probe_client.get("/typed/not-a-number")
    assert response.status_code == 422
    body = response.json()
    assert_envelope(body, "invalid_input")
    details = body["error"]["details"]
    assert details["fields"][0]["location"] == ["path", "number"]
    assert "not-a-number" not in response.text


def test_validation_error_never_echoes_a_password(probe_client: TestClient) -> None:
    response = probe_client.post("/login", json="not-an-object")
    assert response.status_code == 422
    assert_envelope(response.json(), "invalid_input")


def test_unknown_route_is_an_envelope(client: TestClient) -> None:
    response = client.get("/api/no-such-route")
    assert response.status_code == 404
    assert_envelope(response.json(), "not_found")


def test_wrong_method_is_an_envelope(client: TestClient) -> None:
    response = client.post("/api/health")
    assert response.status_code == 405
    assert_envelope(response.json(), "method_not_allowed")
