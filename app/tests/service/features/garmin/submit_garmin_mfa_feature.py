"""Service tests for POST /authenticate-garmin-mfa."""

import uuid

from .submit_garmin_mfa_steps import (
    assert_response_status,
    assert_token_persisted,
    build_submit_mfa_request,
    garmin_accepts_the_mfa_code,
    garmin_is_unreachable,
    garmin_rejects_the_mfa_code,
    mfa_session_is_unknown,
    submit_garmin_mfa,
)


class TestSubmitGarminMfaFeature:
    async def test_submit_garmin_mfa_should_persist_session_when_code_is_valid(
        self, api_client, mocker, garmin_token_persistence_provider
    ):
        # given
        request = build_submit_mfa_request()
        garmin_accepts_the_mfa_code(mocker, "fake-token-data")

        # when
        response = await submit_garmin_mfa(api_client, request)

        # then
        assert_response_status(response, 204)
        await assert_token_persisted(garmin_token_persistence_provider, "fake-token-data")

    async def test_submit_garmin_mfa_should_return_400_when_code_is_missing(self, api_client):
        # when
        response = await api_client.post(
            "/authenticate-garmin-mfa", json={"mfaSessionId": str(uuid.uuid4())}
        )

        # then
        assert_response_status(response, 400)

    async def test_submit_garmin_mfa_should_return_401_when_garmin_rejects_the_code(
        self, api_client, mocker
    ):
        # given
        request = build_submit_mfa_request()
        garmin_rejects_the_mfa_code(mocker)

        # when
        response = await submit_garmin_mfa(api_client, request)

        # then
        assert_response_status(response, 401)

    async def test_submit_garmin_mfa_should_return_409_when_session_is_unknown_or_expired(
        self, api_client, mocker
    ):
        # given
        request = build_submit_mfa_request()
        mfa_session_is_unknown(mocker)

        # when
        response = await submit_garmin_mfa(api_client, request)

        # then
        assert_response_status(response, 409)

    async def test_submit_garmin_mfa_should_return_502_when_garmin_is_unreachable(
        self, api_client, mocker
    ):
        # given
        request = build_submit_mfa_request()
        garmin_is_unreachable(mocker)

        # when
        response = await submit_garmin_mfa(api_client, request)

        # then
        assert_response_status(response, 502)
