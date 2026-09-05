"""Service tests for GET /start/{startDate}/end/{endDate}/activity-summary."""

from datetime import UTC, date, datetime

from .get_strava_activities_steps import an_activity_is_stored
from .get_strava_activity_summary_steps import assert_response_status, get_strava_activity_summary


class TestGetStravaActivitySummaryFeature:
    async def test_get_strava_activity_summary_should_count_all_activity_types_in_total_activities(
        self, api_client, strava_activity_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 20, 8, 0, tzinfo=UTC),
            SportType="Run",
        )
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
            SportType="WeightTraining",
        )

        # when
        response = await get_strava_activity_summary(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["currentPeriod"]["totalActivities"] == 2

    async def test_get_strava_activity_summary_should_only_include_runs_in_distance_and_pace(
        self, api_client, strava_activity_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 20, 8, 0, tzinfo=UTC),
            SportType="Run",
            DistanceMetres=5000.0,
            MovingTimeSeconds=1500,
        )
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
            SportType="WeightTraining",
            DistanceMetres=99999.0,
            MovingTimeSeconds=99999,
        )

        # when
        response = await get_strava_activity_summary(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        current_period = response.json()["currentPeriod"]
        assert current_period["totalActivities"] == 2
        assert current_period["totalRunDistanceMetres"] == 5000.0
        assert current_period["averageRunPaceSecondsPerKm"] == 300.0

    async def test_get_strava_activity_summary_should_compute_pace_as_total_moving_time_over_total_distance_not_average_of_per_activity_paces(  # noqa: E501
        self, api_client, strava_activity_persistence_provider
    ):
        # given: run 1 paces at 300s/km, run 2 paces at 240s/km; a naive average would be
        # 270s/km, but the weighted total (3900s / 15km) is 260s/km
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 20, 8, 0, tzinfo=UTC),
            SportType="Run",
            DistanceMetres=5000.0,
            MovingTimeSeconds=1500,
        )
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
            SportType="Run",
            DistanceMetres=10000.0,
            MovingTimeSeconds=2400,
        )

        # when
        response = await get_strava_activity_summary(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["currentPeriod"]["averageRunPaceSecondsPerKm"] == 260.0

    async def test_get_strava_activity_summary_should_return_null_average_pace_when_period_has_no_runs(  # noqa: E501
        self, api_client, strava_activity_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 20, 8, 0, tzinfo=UTC),
            SportType="WeightTraining",
        )

        # when
        response = await get_strava_activity_summary(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        current_period = response.json()["currentPeriod"]
        assert current_period["totalRunDistanceMetres"] == 0.0
        assert current_period["averageRunPaceSecondsPerKm"] is None

    async def test_get_strava_activity_summary_should_compare_against_the_immediately_preceding_equal_length_period(  # noqa: E501
        self, api_client, strava_activity_persistence_provider
    ):
        # given: a 3-day current period (Aug20-22) has a 3-day prior period of Aug17-19
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=1,
            start_date_local=datetime(2026, 8, 21, 8, 0, tzinfo=UTC),
            SportType="Run",
            DistanceMetres=5000.0,
            MovingTimeSeconds=1500,
        )
        await an_activity_is_stored(
            strava_activity_persistence_provider,
            strava_activity_id=2,
            start_date_local=datetime(2026, 8, 18, 8, 0, tzinfo=UTC),
            SportType="Run",
            DistanceMetres=10000.0,
            MovingTimeSeconds=3000,
        )

        # when
        response = await get_strava_activity_summary(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert body["currentPeriod"]["totalActivities"] == 1
        assert body["currentPeriod"]["totalRunDistanceMetres"] == 5000.0
        assert body["priorPeriod"]["totalActivities"] == 1
        assert body["priorPeriod"]["totalRunDistanceMetres"] == 10000.0

    async def test_get_strava_activity_summary_should_return_400_when_end_date_is_before_start_date(
        self, api_client
    ):
        # when
        response = await get_strava_activity_summary(
            api_client, date(2026, 8, 22), date(2026, 8, 20)
        )

        # then
        assert_response_status(response, 400)
