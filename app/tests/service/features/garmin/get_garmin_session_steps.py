"""Step implementations for the get-Garmin-session service test."""

from datetime import UTC, datetime

import httpx

from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GARMIN_TOKEN_SINGLETON_ID,
    GarminToken,
)
from tests.persistence_providers.garmin_token_persistence_provider import (
    GarminTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.garmin_client import get_garmin_session as _call


async def get_garmin_session(client: httpx.AsyncClient) -> httpx.Response:
    return await _call(client)


async def a_garmin_session_has_been_established(
    persistence_provider: GarminTokenPersistenceProvider, token_data: str = "existing-token"
) -> datetime:
    now = datetime.now(UTC)
    await persistence_provider.insert(
        GarminToken(
            Id=GARMIN_TOKEN_SINGLETON_ID,
            TokenData=token_data,
            CreatedTimestamp=now,
            UpdatedTimestamp=now,
        )
    )
    return now


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code


def assert_response_body(response: httpx.Response, **expected_fields: object) -> None:
    payload = response.json()
    for field, value in expected_fields.items():
        assert payload[field] == value
