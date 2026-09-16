"""Shared fixtures.

The database fixtures skip rather than fail when PostgreSQL is not running, so the
contract and structural suites stay runnable without Docker. Anything that truly
needs a database carries the `db` marker.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from avise.api.app import create_app
from avise.core.config import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def raw_client(app: FastAPI) -> Iterator[TestClient]:
    """A client that surfaces unhandled exceptions instead of the 500 envelope."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def db_engine(settings: Settings):  # type: ignore[no-untyped-def]
    """An engine against the test database, or a skip if PostgreSQL is unreachable."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import OperationalError

    engine = create_engine(settings.test_database_url, future=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PostgreSQL is not reachable for tests: {exc.__class__.__name__}")
    yield engine
    engine.dispose()
