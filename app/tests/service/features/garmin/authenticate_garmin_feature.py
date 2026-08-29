"""Service tests for POST /garmin/authenticate."""

import uuid

from .authenticate_garmin_steps import (
    assert_response_body,
    assert_response_status,
    assert_token_persisted,
    authenticate_garmin,
    build_authenticate_request,
    garmin_accepts_the_credentials,
    garmin_is_unreachable,
    garmin_rejects_the_credentials,
    garmin_requires_mfa,
)


class TestAuthenticateGarminFeature:
    async def test_authenticate_garmin_should_persist_session_when_credentials_are_valid(
        self, api_client, mocker, garmin_token_persistence_provider
    ):
        # given
        request = build_authenticate_request()
        garmin_accepts_the_credentials(mocker, "fake-token-data")

        # when
        response = await authenticate_garmin(api_client, request)

        # then
        assert_response_status(response, 200)
        assert_response_body(response, status="authenticated")
        await assert_token_persisted(garmin_token_persistence_provider, "fake-token-data")

    async def test_authenticate_garmin_should_return_mfa_required_when_garmin_challenges_for_mfa(
        self, api_client, mocker
    ):
        # given
        request = build_authenticate_request()
        mfa_session_id = uuid.uuid4()
        garmin_requires_mfa(mocker, mfa_session_id)

        # when
        response = await authenticate_garmin(api_client, request)

        # then
        assert_response_status(response, 200)
        assert_response_body(response, status="mfa_required", mfaSessionId=str(mfa_session_id))

    async def test_authenticate_garmin_should_return_400_when_email_is_missing(self, api_client):
        # when
        response = await api_client.post("/garmin/authenticate", json={"password": "hunter2"})

        # then
        assert_response_status(response, 400)

    async def test_authenticate_garmin_should_return_401_when_garmin_rejects_credentials(
        self, api_client, mocker
    ):
        # given
        request = build_authenticate_request()
        garmin_rejects_the_credentials(mocker)

        # when
        response = await authenticate_garmin(api_client, request)

        # then
        assert_response_status(response, 401)

    async def test_authenticate_garmin_should_return_502_when_garmin_is_unreachable(
        self, api_client, mocker
    ):
        # given
        request = build_authenticate_request()
        garmin_is_unreachable(mocker)

        # when
        response = await authenticate_garmin(api_client, request)

        # then
        assert_response_status(response, 502)
