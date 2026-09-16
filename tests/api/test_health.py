from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_reports_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "avise",
        "environment": "dev",
    }


def test_health_carries_a_correlation_id(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.headers["X-Request-Id"]
