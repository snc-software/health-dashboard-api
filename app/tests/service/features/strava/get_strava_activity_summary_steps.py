"""Step implementations for the get-Strava-activity-summary service test."""

from datetime import date

import httpx

from tests.service.infrastructure.clients.strava_client import (
    get_strava_activity_summary as _call,
)


async def get_strava_activity_summary(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    return await _call(client, start_date, end_date)


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
