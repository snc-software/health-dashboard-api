"""Step implementations for the fetch-Strava-activities service test."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx
import respx

from health_dashboard_service.contracts.strava import FetchStravaActivitiesRequest
from health_dashboard_service.features.strava.persistence.strava_entities import (
    STRAVA_TOKEN_SINGLETON_ID,
    StravaToken,
)
from tests.persistence_providers.strava_activity_persistence_provider import (
    StravaActivityPersistenceProvider,
)
from tests.persistence_providers.strava_token_persistence_provider import (
    StravaTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.strava_client import fetch_strava_activities as _call
from tests.service.infrastructure.mocks import strava_api_mock


async def fetch_strava_activities(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    return await _call(
        client, FetchStravaActivitiesRequest(start_date=start_date, end_date=end_date)
    )


async def fetch_strava_activities_with_unvalidated_range(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    """Bypasses the contract's own model_validator so an invalid range still reaches the
    server, in order to exercise the endpoint's 400 response."""
    request = FetchStravaActivitiesRequest.model_construct(start_date=start_date, end_date=end_date)
    return await _call(client, request)


async def a_strava_session_has_been_established(
    persistence_provider: StravaTokenPersistenceProvider,
    *,
    access_token: str = "existing-access-token",
    refresh_token: str = "existing-refresh-token",
    expires_at: datetime | None = None,
) -> None:
    now = datetime.now(UTC)
    await persistence_provider.insert(
        StravaToken(
            Id=STRAVA_TOKEN_SINGLETON_ID,
            AccessToken=access_token,
            RefreshToken=refresh_token,
            ExpiresAt=expires_at or (now + timedelta(hours=6)),
            AthleteId=12345678,
            Scope="read,activity:read_all",
            CreatedTimestamp=now,
            UpdatedTimestamp=now,
        )
    )


def build_activity(
    *,
    activity_id: int,
    name: str = "Morning Run",
    type_: str = "Run",
    sport_type: str = "Run",
    start_date: str = "2026-08-20T05:00:00Z",
    start_date_local: str = "2026-08-20T15:00:00Z",
    distance: float = 5000.0,
    moving_time: int = 1500,
    elapsed_time: int = 1600,
    total_elevation_gain: float = 50.0,
    average_heartrate: float | None = 140.0,
    max_heartrate: float | None = 165.0,
    gear_id: str | None = None,
) -> dict[str, Any]:
    return {
        "id": activity_id,
        "name": name,
        "type": type_,
        "sport_type": sport_type,
        "start_date": start_date,
        "start_date_local": start_date_local,
        "distance": distance,
        "moving_time": moving_time,
        "elapsed_time": elapsed_time,
        "total_elevation_gain": total_elevation_gain,
        "average_heartrate": average_heartrate,
        "max_heartrate": max_heartrate,
        "gear_id": gear_id,
    }


def strava_returns_activities(
    respx_mock: respx.MockRouter, activities: list[dict[str, Any]]
) -> None:
    strava_api_mock.configure_successful_activities_list(respx_mock, activities)


def strava_returns_activities_across_two_syncs(
    respx_mock: respx.MockRouter,
    first_sync: list[dict[str, Any]],
    second_sync: list[dict[str, Any]],
) -> None:
    strava_api_mock.configure_activities_list_sequence(respx_mock, [first_sync, second_sync])


def strava_returns_activities_for_access_token(
    respx_mock: respx.MockRouter, *, access_token: str, activities: list[dict[str, Any]]
) -> None:
    strava_api_mock.configure_activities_list_for_access_token(
        respx_mock, access_token=access_token, activities=activities
    )


def strava_is_unreachable_for_activities(respx_mock: respx.MockRouter) -> None:
    strava_api_mock.configure_activities_list_unreachable(respx_mock)


def strava_refreshes_the_token_successfully(
    respx_mock: respx.MockRouter, *, access_token: str, refresh_token: str
) -> None:
    strava_api_mock.configure_successful_token_refresh(
        respx_mock,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=int((datetime.now(UTC) + timedelta(hours=6)).timestamp()),
    )


async def assert_activity_persisted(
    persistence_provider: StravaActivityPersistenceProvider,
    activity_id: int,
    **expected_fields: Any,
) -> None:
    row = await persistence_provider.get_by_strava_activity_id(activity_id)
    assert row is not None
    for field, value in expected_fields.items():
        assert getattr(row, field) == value


async def assert_no_activity_persisted(
    persistence_provider: StravaActivityPersistenceProvider, activity_id: int
) -> None:
    assert await persistence_provider.get_by_strava_activity_id(activity_id) is None


async def the_stored_strava_token(
    persistence_provider: StravaTokenPersistenceProvider,
) -> StravaToken | None:
    return await persistence_provider.get_by_id(STRAVA_TOKEN_SINGLETON_ID)


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
