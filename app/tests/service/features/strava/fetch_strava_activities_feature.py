"""Service tests for POST /strava-activities."""

from datetime import UTC, date, datetime, timedelta

from .fetch_strava_activities_steps import (
    a_strava_session_has_been_established,
    assert_activity_persisted,
    assert_no_activity_persisted,
    assert_response_status,
    build_activity,
    fetch_strava_activities,
    fetch_strava_activities_with_unvalidated_range,
    strava_is_unreachable_for_activities,
    strava_refreshes_the_token_successfully,
    strava_returns_activities,
    strava_returns_activities_across_two_syncs,
    strava_returns_activities_for_access_token,
    the_stored_strava_token,
)


class TestFetchStravaActivitiesFeature:
    async def test_fetch_strava_activities_should_persist_every_returned_activity_and_return_counts_by_type(  # noqa: E501
        self,
        api_client,
        strava_token_persistence_provider,
        strava_activity_persistence_provider,
        respx_mock,
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        activities = [
            build_activity(activity_id=1, type_="Run", sport_type="Run"),
            build_activity(activity_id=2, type_="WeightTraining", sport_type="WeightTraining"),
            build_activity(activity_id=3, type_="Workout", sport_type="Workout"),
        ]
        await a_strava_session_has_been_established(strava_token_persistence_provider)
        strava_returns_activities(respx_mock, activities)

        # when
        response = await fetch_strava_activities(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["countsByType"] == {"Run": 1, "WeightTraining": 1, "Workout": 1}
        await assert_activity_persisted(
            strava_activity_persistence_provider, 1, Name="Morning Run", SportType="Run"
        )
        await assert_activity_persisted(
            strava_activity_persistence_provider, 2, SportType="WeightTraining"
        )
        await assert_activity_persisted(
            strava_activity_persistence_provider, 3, SportType="Workout"
        )

    async def test_fetch_strava_activities_should_refresh_an_expired_access_token_before_calling_strava(  # noqa: E501
        self,
        api_client,
        strava_token_persistence_provider,
        strava_activity_persistence_provider,
        respx_mock,
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await a_strava_session_has_been_established(
            strava_token_persistence_provider,
            access_token="stale-access-token",
            refresh_token="stale-refresh-token",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
        strava_refreshes_the_token_successfully(
            respx_mock,
            access_token="refreshed-access-token",
            refresh_token="refreshed-refresh-token",
        )
        strava_returns_activities_for_access_token(
            respx_mock,
            access_token="refreshed-access-token",
            activities=[build_activity(activity_id=1)],
        )

        # when
        response = await fetch_strava_activities(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        stored_token = await the_stored_strava_token(strava_token_persistence_provider)
        assert stored_token is not None
        assert stored_token.AccessToken == "refreshed-access-token"
        assert stored_token.RefreshToken == "refreshed-refresh-token"

    async def test_fetch_strava_activities_should_return_400_when_no_strava_session_has_been_established(  # noqa: E501
        self, api_client, respx_mock
    ):
        # when
        response = await fetch_strava_activities(api_client, date(2026, 8, 20), date(2026, 8, 22))

        # then
        assert_response_status(response, 400)
        assert len(respx_mock.calls) == 0

    async def test_fetch_strava_activities_should_overwrite_an_existing_activity_row_when_synced_again(  # noqa: E501
        self,
        api_client,
        strava_token_persistence_provider,
        strava_activity_persistence_provider,
        respx_mock,
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await a_strava_session_has_been_established(strava_token_persistence_provider)
        strava_returns_activities_across_two_syncs(
            respx_mock,
            [build_activity(activity_id=1, name="First Sync")],
            [build_activity(activity_id=1, name="Second Sync")],
        )

        # when: synced once, then synced again with different field values for the same id
        first_response = await fetch_strava_activities(api_client, start_date, end_date)
        assert_response_status(first_response, 200)
        second_response = await fetch_strava_activities(api_client, start_date, end_date)

        # then
        assert_response_status(second_response, 200)
        await assert_activity_persisted(strava_activity_persistence_provider, 1, Name="Second Sync")

    async def test_fetch_strava_activities_should_return_400_when_end_date_is_before_start_date(
        self, api_client
    ):
        # when
        response = await fetch_strava_activities_with_unvalidated_range(
            api_client, date(2026, 8, 22), date(2026, 8, 20)
        )

        # then
        assert_response_status(response, 400)

    async def test_fetch_strava_activities_should_return_502_when_strava_is_unreachable(
        self,
        api_client,
        strava_token_persistence_provider,
        strava_activity_persistence_provider,
        respx_mock,
    ):
        # given
        await a_strava_session_has_been_established(strava_token_persistence_provider)
        strava_is_unreachable_for_activities(respx_mock)

        # when
        response = await fetch_strava_activities(api_client, date(2026, 8, 20), date(2026, 8, 22))

        # then
        assert_response_status(response, 502)
        await assert_no_activity_persisted(strava_activity_persistence_provider, 1)
