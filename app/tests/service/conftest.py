"""Re-exports `tests/service/infrastructure/service_application.py`'s fixtures
(Postgres TestContainer, FastAPI app, api_client, persistence providers) so pytest
picks them up for every test under `tests/service/`, per `service-test-standards.md`.
Scoped to this subtree (rather than a root-level `pytest_plugins`) so plain
unit-test runs never require Docker/`goose`."""

from tests.service.infrastructure.service_application import (  # noqa: F401
    _reset_garmin_tables,
    _reset_strava_tables,
    api_client,
    garmin_daily_stat_persistence_provider,
    garmin_token_persistence_provider,
    postgres_container,
    postgres_engine,
    service_app,
    strava_activity_persistence_provider,
    strava_token_persistence_provider,
    test_settings,
)
