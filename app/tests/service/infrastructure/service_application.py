"""Builds the FastAPI app + Postgres TestContainer for service tests.

The Postgres container and its migrations are built once per test session;
the FastAPI app (and its engine) is rebuilt per test function to keep fixture
wiring simple, and `GarminTokens`/`GarminDailyStats` are truncated before every
test so the shared container never leaks state between tests.
"""

import os
import shutil
import subprocess
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.community.postgres import PostgresContainer

# `health_dashboard_service.main` builds a module-level `app = create_app()` via
# `get_settings()`, which requires PG_* env vars to be set. These placeholders let that
# import succeed without a real `.env`; `service_app` below always rebuilds its own app
# against the real container settings, so this instance is never actually used.
os.environ.setdefault("PG_HOST", "localhost")
os.environ.setdefault("PG_USER", "test")
os.environ.setdefault("PG_PASSWORD", "test")
os.environ.setdefault("PG_DATABASE", "test")
os.environ.setdefault("STRAVA_CLIENT_ID", "test-strava-client-id")
os.environ.setdefault("STRAVA_CLIENT_SECRET", "test-strava-client-secret")
os.environ.setdefault("STRAVA_REDIRECT_URI", "http://localhost:8000/strava-callback")
os.environ.setdefault("STRAVA_UI_REDIRECT_URL", "http://localhost:5173/settings/strava")
os.environ.setdefault("STRAVA_SCOPE", '["read","activity:read_all"]')

from health_dashboard_service import config, main
from tests.persistence_providers.garmin_daily_stat_persistence_provider import (
    GarminDailyStatPersistenceProvider,
)
from tests.persistence_providers.garmin_token_persistence_provider import (
    GarminTokenPersistenceProvider,
)
from tests.persistence_providers.strava_token_persistence_provider import (
    StravaTokenPersistenceProvider,
)

from .settings import build_test_engine, build_test_settings

_MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations"


def _apply_migrations(container: PostgresContainer) -> None:
    dsn = (
        f"postgres://{container.username}:{container.password}"
        f"@{container.get_container_host_ip()}:{container.get_exposed_port(container.port)}"
        f"/{container.dbname}"
    )
    goose = shutil.which("goose")
    if goose is None:
        raise RuntimeError("`goose` is required on PATH to run service tests.")

    subprocess.run(  # noqa: S603 — `goose` resolved via shutil.which(), not user input
        [goose, "up"],
        cwd=_MIGRATIONS_DIR,
        env={**os.environ, "GOOSE_DRIVER": "postgres", "GOOSE_DBSTRING": dsn},
        check=True,
    )


@pytest.fixture(scope="session")
def postgres_container() -> AsyncGenerator[PostgresContainer]:  # type: ignore[misc]
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as container:
        _apply_migrations(container)
        yield container


@pytest.fixture(scope="session")
def test_settings(postgres_container: PostgresContainer) -> config.Settings:
    return build_test_settings(postgres_container)


@pytest_asyncio.fixture
async def postgres_engine(test_settings: config.Settings) -> AsyncGenerator[AsyncEngine]:
    engine = build_test_engine(test_settings)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _reset_garmin_tables(postgres_engine: AsyncEngine) -> None:
    async with postgres_engine.begin() as connection:
        await connection.execute(
            text('TRUNCATE TABLE public."GarminTokens", public."GarminDailyStats"')
        )


@pytest_asyncio.fixture(autouse=True)
async def _reset_strava_tables(postgres_engine: AsyncEngine) -> None:
    async with postgres_engine.begin() as connection:
        await connection.execute(text('TRUNCATE TABLE public."StravaTokens"'))


@pytest.fixture
def garmin_token_persistence_provider(
    postgres_engine: AsyncEngine,
) -> GarminTokenPersistenceProvider:
    return GarminTokenPersistenceProvider(postgres_engine)


@pytest.fixture
def garmin_daily_stat_persistence_provider(
    postgres_engine: AsyncEngine,
) -> GarminDailyStatPersistenceProvider:
    return GarminDailyStatPersistenceProvider(postgres_engine)


@pytest.fixture
def strava_token_persistence_provider(
    postgres_engine: AsyncEngine,
) -> StravaTokenPersistenceProvider:
    return StravaTokenPersistenceProvider(postgres_engine)


@pytest_asyncio.fixture
async def service_app(
    test_settings: config.Settings, monkeypatch: pytest.MonkeyPatch
) -> AsyncGenerator[FastAPI]:
    # `get_settings()` is called via several independent `from .config import
    # get_settings` bindings (main.py, routes/, infrastructure/postgres/), all of which
    # share the one `@lru_cache`-wrapped function object — so pointing every one of them
    # at the container is done by setting the env vars they all resolve from, then
    # clearing that one shared cache, rather than patching any single name binding.
    monkeypatch.setenv("PG_HOST", test_settings.pg_host)
    monkeypatch.setenv("PG_PORT", str(test_settings.pg_port))
    monkeypatch.setenv("PG_USER", test_settings.pg_user)
    monkeypatch.setenv("PG_PASSWORD", test_settings.pg_password)
    monkeypatch.setenv("PG_DATABASE", test_settings.pg_database)
    monkeypatch.setenv("ENVIRONMENT", "test")
    config.get_settings.cache_clear()

    app = main.create_app()
    async with app.router.lifespan_context(app):
        yield app

    config.get_settings.cache_clear()


@pytest_asyncio.fixture
async def api_client(service_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=service_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
