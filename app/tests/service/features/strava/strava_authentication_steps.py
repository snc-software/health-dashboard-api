"""Step implementations for the Strava authentication service test."""

from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import httpx
import respx

from health_dashboard_service.features.strava.persistence.strava_entities import (
    STRAVA_TOKEN_SINGLETON_ID,
    StravaToken,
)
from tests.persistence_providers.strava_token_persistence_provider import (
    StravaTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.strava_client import authorize_strava as _authorize
from tests.service.infrastructure.clients.strava_client import get_strava_session as _get_session
from tests.service.infrastructure.clients.strava_client import strava_callback as _callback
from tests.service.infrastructure.mocks import strava_api_mock


async def authorize_strava(client: httpx.AsyncClient) -> httpx.Response:
    return await _authorize(client)


async def a_pending_strava_authorization_has_been_started(client: httpx.AsyncClient) -> str:
    """Hit /authorize-strava and return the generated `state` from its redirect."""
    response = await _authorize(client)
    query = parse_qs(urlparse(response.headers["location"]).query)
    return query["state"][0]


async def strava_callback(
    client: httpx.AsyncClient,
    *,
    code: str | None = None,
    scope: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> httpx.Response:
    return await _callback(client, code=code, scope=scope, state=state, error=error)


async def get_strava_session(client: httpx.AsyncClient) -> httpx.Response:
    return await _get_session(client)


async def a_strava_token_has_been_stored(
    persistence_provider: StravaTokenPersistenceProvider, *, athlete_id: int = 12345678
) -> datetime:
    now = datetime.now(UTC)
    await persistence_provider.insert(
        StravaToken(
            Id=STRAVA_TOKEN_SINGLETON_ID,
            AccessToken="existing-access-token",
            RefreshToken="existing-refresh-token",
            ExpiresAt=now,
            AthleteId=athlete_id,
            Scope="read,activity:read_all",
            CreatedTimestamp=now,
            UpdatedTimestamp=now,
        )
    )
    return now


def configure_successful_strava_exchange_and_verification(
    respx_mock: respx.MockRouter, *, access_token: str, refresh_token: str, athlete_id: int
) -> None:
    strava_api_mock.configure_successful_token_exchange(
        respx_mock,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=int(datetime.now(UTC).timestamp()) + 21600,
        athlete_id=athlete_id,
    )
    strava_api_mock.configure_successful_athlete_verification(respx_mock, athlete_id=athlete_id)


async def the_stored_strava_token(
    persistence_provider: StravaTokenPersistenceProvider,
) -> StravaToken | None:
    return await persistence_provider.get_by_id(STRAVA_TOKEN_SINGLETON_ID)


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code


def assert_redirect_location_contains(response: httpx.Response, *fragments: str) -> None:
    location = response.headers["location"]
    for fragment in fragments:
        assert fragment in location


def assert_response_body(response: httpx.Response, **expected_fields: object) -> None:
    payload = response.json()
    for field, value in expected_fields.items():
        assert payload[field] == value
