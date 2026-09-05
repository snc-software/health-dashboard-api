"""Service tests for GET /start/{startDate}/end/{endDate}/activities."""

from datetime import UTC, date, datetime

from .get_strava_activities_steps import (
    an_activity_is_stored,
    assert_response_status,
    get_strava_activities,
)


class TestGetStravaActivitiesFeature:
    async def test_get_strava_activities_should_return_stored_activities_in_range_ordered_by_start_date(  # noqa: E501
        self, api_client, strava_activity_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        last = await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=3,
            start_date_local=datetime(2026, 8, 22, 8, 0, tzinfo=UTC),
        )
        first = await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 20, 8, 0, tzinfo=UTC),
        )
        middle = await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
        )

        # when
        response = await get_strava_activities(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert [row["stravaActivityId"] for row in body] == [
            first.StravaActivityId,
            middle.StravaActivityId,
            last.StravaActivityId,
        ]

    async def test_get_strava_activities_should_omit_activities_outside_the_range(
        self, api_client, strava_activity_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 19, 8, 0, tzinfo=UTC),
        )
        in_range = await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
        )
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=3,
            start_date_local=datetime(2026, 8, 23, 8, 0, tzinfo=UTC),
        )

        # when
        response = await get_strava_activities(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert [row["stravaActivityId"] for row in body] == [in_range.StravaActivityId]

    async def test_get_strava_activities_should_filter_by_local_activity_date_not_utc_date(
        self, api_client, strava_activity_persistence_provider
    ):
        # given: an activity started at 00:30 local time on the 5th, which (per Strava's
        # convention) is still 13:30 UTC on the 4th — the Australia-run scenario from plan
        # review, where only matching on local date recovers the athlete's true activity date.
        activity = await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date=datetime(2026, 8, 4, 13, 30, tzinfo=UTC),
            start_date_local=datetime(2026, 8, 5, 0, 30, tzinfo=UTC),
        )

        # when
        response = await get_strava_activities(api_client, date(2026, 8, 5), date(2026, 8, 5))

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert [row["stravaActivityId"] for row in body] == [activity.StravaActivityId]

    async def test_get_strava_activities_should_return_empty_list_when_nothing_is_stored(
        self, api_client
    ):
        # when
        response = await get_strava_activities(api_client, date(2026, 8, 20), date(2026, 8, 22))

        # then
        assert_response_status(response, 200)
        assert response.json() == []

    async def test_get_strava_activities_should_return_400_when_end_date_is_before_start_date(
        self, api_client
    ):
        # when
        response = await get_strava_activities(api_client, date(2026, 8, 22), date(2026, 8, 20))

        # then
        assert_response_status(response, 400)
