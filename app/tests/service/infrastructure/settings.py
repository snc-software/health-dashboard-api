"""Test settings and Postgres connection helpers, resolved against the shared
session Postgres TestContainer (see `service_application.py`)."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from health_dashboard_service.config import Settings
from health_dashboard_service.infrastructure.postgres.connection_factory import build_dsn


def build_test_settings(container: PostgresContainer) -> Settings:
    """Build app Settings pointed at the shared session Postgres TestContainer."""
    return Settings(
        pg_host=container.get_container_host_ip(),
        pg_port=int(container.get_exposed_port(container.port)),
        pg_user=container.username,
        pg_password=container.password,
        pg_database=container.dbname,
        environment="test",
    )


def build_test_engine(settings: Settings) -> AsyncEngine:
    """Build a standalone async engine for test-only direct DB access (persistence providers)."""
    return create_async_engine(build_dsn(settings))
