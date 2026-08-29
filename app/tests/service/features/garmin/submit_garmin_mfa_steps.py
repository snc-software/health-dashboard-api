"""Step implementations for the submit-Garmin-MFA service test."""

import uuid

import httpx
from pytest_mock import MockerFixture

from health_dashboard_service.contracts.garmin import SubmitGarminMfaRequest
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GARMIN_TOKEN_SINGLETON_ID,
)
from tests.persistence_providers.garmin_token_persistence_provider import (
    GarminTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.garmin_client import submit_garmin_mfa as _call
from tests.service.infrastructure.mocks import garmin_api_mock


def build_submit_mfa_request(
    mfa_session_id: uuid.UUID | None = None, code: str = "123456"
) -> SubmitGarminMfaRequest:
    return SubmitGarminMfaRequest(mfa_session_id=mfa_session_id or uuid.uuid4(), code=code)


async def submit_garmin_mfa(
    client: httpx.AsyncClient, request: SubmitGarminMfaRequest
) -> httpx.Response:
    return await _call(client, request)


def garmin_accepts_the_mfa_code(mocker: MockerFixture, token_data: str) -> None:
    garmin_api_mock.configure_successful_mfa_completion(mocker, token_data)


def garmin_rejects_the_mfa_code(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_mfa_rejected(mocker)


def mfa_session_is_unknown(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_mfa_session_unknown(mocker)


def garmin_is_unreachable(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_mfa_completion_unreachable(mocker)


async def assert_token_persisted(
    persistence_provider: GarminTokenPersistenceProvider, token_data: str
) -> None:
    row = await persistence_provider.get_by_id(GARMIN_TOKEN_SINGLETON_ID)
    assert row is not None
    assert row.TokenData == token_data


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
