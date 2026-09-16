"""Application configuration. Every value is environment-driven; nothing secret is defaulted."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from the environment, prefixed AVISE_."""

    model_config = SettingsConfigDict(
        env_prefix="AVISE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "dev"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://avise:avise@localhost:5432/avise"
    test_database_url: str = "postgresql+psycopg://avise:avise@localhost:5432/avise_test"

    # CORS is locked to a single dev origin. A list would invite widening it.
    cors_origin: str = "http://localhost:5173"

    # Sessions - report section 22.
    session_cookie_name: str = "avise_session"
    session_ttl_hours: int = 8
    session_cookie_secure: bool = True

    # Login protection - PHASE-0-DECISIONS E1.
    login_max_attempts: int = 5
    login_attempt_window_minutes: int = 15
    login_lockout_minutes: int = 15
    rate_limit_login_per_ip_per_minute: int = 10

    # Passwords - length only, no composition rules.
    password_min_length: int = 12
    argon2_time_cost: int = 3
    argon2_memory_cost_kib: int = 65536
    argon2_parallelism: int = 4

    # Evidence files live outside any served static route.
    upload_dir: Path = Path("./uploads")
    max_upload_mb: int = 25

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
