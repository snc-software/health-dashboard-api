"""Service tests for the Strava OAuth authentication flow: GET /authorize-strava,
GET /strava-callback, GET /strava-session."""

from datetime import datetime

from tests.service.infrastructure.mocks import strava_api_mock

from .strava_authentication_steps import (
    a_pending_strava_authorization_has_been_started,
    a_strava_token_has_been_stored,
    assert_redirect_location_contains,
    assert_response_body,
    assert_response_status,
    authorize_strava,
    configure_successful_strava_exchange_and_verification,
    get_strava_session,
    strava_callback,
    the_stored_strava_token,
)


class TestStravaAuthenticationFeature:
    async def test_authorize_strava_should_redirect_to_strava_with_client_id_scope_and_a_generated_state(  # noqa: E501
        self, api_client
    ):
        # when
        response = await authorize_strava(api_client)

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(
            response,
            "https://www.strava.com/oauth/authorize",
            "client_id=",
            "scope=read%2Cactivity%3Aread_all",
            "state=",
        )

    async def test_strava_callback_should_persist_a_token_row_and_redirect_with_connected_true_on_success(  # noqa: E501
        self, api_client, strava_token_persistence_provider, respx_mock
    ):
        # given
        state = await a_pending_strava_authorization_has_been_started(api_client)
        configure_successful_strava_exchange_and_verification(
            respx_mock,
            access_token="new-access-token",
            refresh_token="new-refresh-token",
            athlete_id=987654,
        )

        # when
        response = await strava_callback(api_client, code="auth-code", state=state)

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=true")
        stored = await the_stored_strava_token(strava_token_persistence_provider)
        assert stored is not None
        assert stored.AccessToken == "new-access-token"
        assert stored.RefreshToken == "new-refresh-token"
        assert stored.AthleteId == 987654

    async def test_strava_callback_should_redirect_with_connected_false_when_state_is_missing_or_unknown(  # noqa: E501
        self, api_client
    ):
        # when / then: no state at all
        response = await strava_callback(api_client, code="auth-code")
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=false")

        # when / then: an unknown state
        response = await strava_callback(api_client, code="auth-code", state="unknown-state")
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=false")

    async def test_strava_callback_should_redirect_with_connected_false_when_strava_reports_an_error(  # noqa: E501
        self, api_client
    ):
        # when
        response = await strava_callback(api_client, error="access_denied")

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=false")

    async def test_strava_callback_should_redirect_with_connected_false_when_token_exchange_fails(
        self, api_client, strava_token_persistence_provider, respx_mock
    ):
        # given
        state = await a_pending_strava_authorization_has_been_started(api_client)
        strava_api_mock.configure_token_exchange_rejected(respx_mock)

        # when
        response = await strava_callback(api_client, code="auth-code", state=state)

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=false")
        assert await the_stored_strava_token(strava_token_persistence_provider) is None

    async def test_strava_callback_should_redirect_with_connected_false_when_verification_call_fails(  # noqa: E501
        self, api_client, strava_token_persistence_provider, respx_mock
    ):
        # given
        state = await a_pending_strava_authorization_has_been_started(api_client)
        strava_api_mock.configure_successful_token_exchange(
            respx_mock,
            access_token="new-access-token",
            refresh_token="new-refresh-token",
            expires_at=9999999999,
            athlete_id=987654,
        )
        strava_api_mock.configure_athlete_verification_rejected(respx_mock)

        # when
        response = await strava_callback(api_client, code="auth-code", state=state)

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=false")
        assert await the_stored_strava_token(strava_token_persistence_provider) is None

    async def test_strava_callback_should_overwrite_existing_token_row_when_authorizing_again(
        self, api_client, strava_token_persistence_provider, respx_mock
    ):
        # given
        await a_strava_token_has_been_stored(strava_token_persistence_provider, athlete_id=111)
        state = await a_pending_strava_authorization_has_been_started(api_client)
        configure_successful_strava_exchange_and_verification(
            respx_mock,
            access_token="refreshed-access-token",
            refresh_token="refreshed-refresh-token",
            athlete_id=222,
        )

        # when
        response = await strava_callback(api_client, code="auth-code", state=state)

        # then
        assert_response_status(response, 307)
        assert_redirect_location_contains(response, "stravaConnected=true")
        stored = await the_stored_strava_token(strava_token_persistence_provider)
        assert stored is not None
        assert stored.AccessToken == "refreshed-access-token"
        assert stored.AthleteId == 222

    async def test_get_strava_session_should_report_connected_false_when_no_token_is_stored(
        self, api_client
    ):
        # when
        response = await get_strava_session(api_client)

        # then
        assert_response_status(response, 200)
        assert_response_body(response, connected=False, athleteId=None, updatedTimestamp=None)

    async def test_get_strava_session_should_report_connected_true_with_athlete_id_and_timestamp_when_a_token_is_stored(  # noqa: E501
        self, api_client, strava_token_persistence_provider
    ):
        # given
        established_at = await a_strava_token_has_been_stored(
            strava_token_persistence_provider, athlete_id=555
        )

        # when
        response = await get_strava_session(api_client)

        # then
        assert_response_status(response, 200)
        payload = response.json()
        assert payload["connected"] is True
        assert payload["athleteId"] == 555
        assert datetime.fromisoformat(payload["updatedTimestamp"]) == established_at
