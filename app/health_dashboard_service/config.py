from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    """Application settings, resolved from the environment and a local .env file."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Health Dashboard API"
    app_version: str = "1.0.0"
    environment: str = Field("development", description="development | staging | production")

    log_level: str = "INFO"

    cors_allow_origins: list[str] = Field(default_factory=list)
    cors_allow_credentials: bool = False
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])

    pg_host: str
    pg_port: int = 5432
    pg_user: str
    pg_password: str
    pg_database: str

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = Field(1800, description="Recycle pooled connections after N seconds")
    db_echo: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()
