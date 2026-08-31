"""Service tests for GET /garmin-session."""

from datetime import datetime

from .get_garmin_session_steps import (
    a_garmin_session_has_been_established,
    assert_response_body,
    assert_response_status,
    get_garmin_session,
)


class TestGetGarminSessionFeature:
    async def test_get_garmin_session_should_return_unauthenticated_when_no_token_is_stored(
        self, api_client
    ):
        # when
        response = await get_garmin_session(api_client)

        # then
        assert_response_status(response, 200)
        assert_response_body(response, status="unauthenticated", authenticatedAt=None)

    async def test_get_garmin_session_should_return_authenticated_when_token_is_stored(
        self, api_client, garmin_token_persistence_provider
    ):
        # given
        established_at = await a_garmin_session_has_been_established(
            garmin_token_persistence_provider
        )

        # when
        response = await get_garmin_session(api_client)

        # then
        assert_response_status(response, 200)
        payload = response.json()
        assert payload["status"] == "authenticated"
        assert datetime.fromisoformat(payload["authenticatedAt"]) == established_at

    async def test_get_garmin_session_should_never_include_token_data_in_response(
        self, api_client, garmin_token_persistence_provider
    ):
        # given
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)

        # when
        response = await get_garmin_session(api_client)

        # then
        payload = response.json()
        assert "tokenData" not in payload
        assert "TokenData" not in payload
