"""
Centralised configuration using Pydantic BaseSettings.
Values are loaded from environment variables or a .env file.
Override per environment by setting ENV=staging|prod.
"""
from functools import lru_cache
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────────────
    env: str = Field(default="dev", description="dev | staging | prod")

    # ── API Under Test ───────────────────────────────────────────
    base_url: str = Field(
        default="https://restful-booker.herokuapp.com",
        description="Base URL for the Restful-Booker API",
    )

    # ── UI Under Test ────────────────────────────────────────────
    ui_base_url: str = Field(
        default="https://automationintesting.online",
        description="Base URL for the booking UI",
    )

    # ── Auth Credentials ─────────────────────────────────────────
    admin_username: str = Field(default="admin")
    admin_password: str = Field(default="password")

    # ── Browser Settings ─────────────────────────────────────────
    browser: str = Field(default="chromium", description="chromium | firefox | webkit")
    headless: bool = Field(default=True)
    slow_mo: int = Field(default=0, description="Milliseconds to slow Playwright actions")
    browser_timeout: int = Field(default=30_000, description="Default timeout in ms")

    # ── Database ─────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./reports/test_shadow.db",
        description="SQLAlchemy connection string for shadow DB",
    )

    # ── Retry / Resilience ───────────────────────────────────────
    api_retry_attempts: int = Field(default=3)
    api_retry_wait: float = Field(default=1.0, description="Seconds between retries")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()


settings = get_settings()
