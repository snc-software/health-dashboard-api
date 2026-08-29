"""Step implementations for the authenticate-Garmin service test."""

import httpx
from pytest_mock import MockerFixture

from health_dashboard_service.contracts.garmin import AuthenticateGarminRequest
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GARMIN_TOKEN_SINGLETON_ID,
)
from tests.persistence_providers.garmin_token_persistence_provider import (
    GarminTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.garmin_client import authenticate_garmin as _call
from tests.service.infrastructure.mocks import garmin_api_mock


def build_authenticate_request(
    email: str = "athlete@example.com", password: str = "hunter2"
) -> AuthenticateGarminRequest:
    return AuthenticateGarminRequest(email=email, password=password)


async def authenticate_garmin(
    client: httpx.AsyncClient, request: AuthenticateGarminRequest
) -> httpx.Response:
    return await _call(client, request)


def garmin_accepts_the_credentials(mocker: MockerFixture, token_data: str) -> None:
    garmin_api_mock.configure_successful_login(mocker, token_data)


def garmin_rejects_the_credentials(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_login_rejected(mocker)


def garmin_is_unreachable(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_login_unreachable(mocker)


async def assert_token_persisted(
    persistence_provider: GarminTokenPersistenceProvider, token_data: str
) -> None:
    row = await persistence_provider.get_by_id(GARMIN_TOKEN_SINGLETON_ID)
    assert row is not None
    assert row.TokenData == token_data


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
