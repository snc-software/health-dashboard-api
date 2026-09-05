"""Step implementations for the get-Strava-activities service test."""

from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid7

import httpx

from health_dashboard_service.features.strava.persistence.strava_entities import StravaActivity
from tests.persistence_providers.strava_activity_persistence_provider import (
    StravaActivityPersistenceProvider,
)
from tests.service.infrastructure.clients.strava_client import get_strava_activities as _call


async def get_strava_activities(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    return await _call(client, start_date, end_date)


async def an_activity_is_stored(
    persistence_provider: StravaActivityPersistenceProvider,
    *,
    strava_activity_id: int,
    start_date_local: datetime,
    start_date: datetime | None = None,
    **overrides: Any,
) -> StravaActivity:
    fields: dict[str, Any] = {
        "Id": uuid7(),
        "StravaActivityId": strava_activity_id,
        "Name": "Morning Run",
        "Type": "Run",
        "SportType": "Run",
        "StartDate": start_date if start_date is not None else start_date_local,
        "StartDateLocal": start_date_local,
        "DistanceMetres": 5000.0,
        "MovingTimeSeconds": 1500,
        "ElapsedTimeSeconds": 1600,
        "TotalElevationGainMetres": 50.0,
        "AverageHeartrate": 140.0,
        "MaxHeartrate": 165.0,
        "GearId": None,
        "UpdatedTimestamp": datetime.now(UTC),
    }
    fields.update(overrides)
    activity = StravaActivity(**fields)
    await persistence_provider.insert(activity)
    return activity


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
