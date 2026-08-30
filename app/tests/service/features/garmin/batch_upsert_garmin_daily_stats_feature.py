"""Service tests for POST /batch-garmin-daily-stats."""

from datetime import date

from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminDailySnapshot,
)

from .batch_upsert_garmin_daily_stats_steps import (
    a_daily_stat_is_already_stored,
    assert_daily_stat_persisted,
    assert_no_daily_stat_persisted,
    assert_response_status,
    batch_upsert_garmin_daily_stats,
    batch_upsert_garmin_daily_stats_with_unvalidated_range,
    garmin_fails_for_some_dates,
    garmin_returns_daily_stats,
    spy_on_fetch_daily_snapshot,
)
from .upsert_garmin_daily_stat_steps import a_garmin_session_has_been_established


class TestBatchUpsertGarminDailyStatsFeature:
    async def test_batch_upsert_garmin_daily_stats_should_persist_a_row_for_every_date_in_range(
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        start_date = date(2026, 8, 20)
        end_date = date(2026, 8, 22)
        snapshots = {
            date(2026, 8, 20): GarminDailySnapshot(
                steps=8500,
                resting_heart_rate=52,
                sleep_seconds=25200,
                peak_body_battery=68,
                sleep_score=85,
                hrv_last_night_average=45,
                hrv_status="BALANCED",
                training_readiness_score=72,
                training_status="PRODUCTIVE",
                vo2_max=45,
                fitness_age=32.5,
                weight_grams=70500,
                intensity_minutes=35,
            ),
            date(2026, 8, 21): GarminDailySnapshot(
                steps=9000,
                resting_heart_rate=50,
                sleep_seconds=26000,
                peak_body_battery=70,
                sleep_score=88,
                hrv_last_night_average=47,
                hrv_status="BALANCED",
                training_readiness_score=75,
                training_status="PRODUCTIVE",
                vo2_max=46,
                fitness_age=32.0,
                weight_grams=70400,
                intensity_minutes=40,
            ),
            date(2026, 8, 22): GarminDailySnapshot(
                steps=7000,
                resting_heart_rate=54,
                sleep_seconds=24000,
                peak_body_battery=60,
                sleep_score=80,
                hrv_last_night_average=42,
                hrv_status="BALANCED",
                training_readiness_score=65,
                training_status="MAINTAINING",
                vo2_max=44,
                fitness_age=33.0,
                weight_grams=70600,
                intensity_minutes=25,
            ),
        }
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_returns_daily_stats(mocker, snapshots)

        # when
        response = await batch_upsert_garmin_daily_stats(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["failedDates"] == []
        for stat_date, snapshot in snapshots.items():
            await assert_daily_stat_persisted(
                garmin_daily_stat_persistence_provider, stat_date, snapshot
            )

    async def test_batch_upsert_garmin_daily_stats_should_return_400_when_end_date_is_before_start_date(  # noqa: E501
        self, api_client
    ):
        # when
        response = await batch_upsert_garmin_daily_stats_with_unvalidated_range(
            api_client, date(2026, 8, 22), date(2026, 8, 20)
        )

        # then
        assert_response_status(response, 400)

    async def test_batch_upsert_garmin_daily_stats_should_persist_other_dates_when_one_day_in_range_fails(  # noqa: E501
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        start_date = date(2026, 8, 20)
        failing_date = date(2026, 8, 21)
        end_date = date(2026, 8, 22)
        snapshot = GarminDailySnapshot(
            steps=8500,
            resting_heart_rate=52,
            sleep_seconds=25200,
            peak_body_battery=68,
            sleep_score=85,
            hrv_last_night_average=45,
            hrv_status="BALANCED",
            training_readiness_score=72,
            training_status="PRODUCTIVE",
            vo2_max=45,
            fitness_age=32.5,
            weight_grams=70500,
            intensity_minutes=35,
        )
        snapshots = {start_date: snapshot, failing_date: snapshot, end_date: snapshot}
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_fails_for_some_dates(mocker, snapshots, {failing_date})

        # when
        response = await batch_upsert_garmin_daily_stats(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["failedDates"] == [failing_date.isoformat()]
        await assert_daily_stat_persisted(
            garmin_daily_stat_persistence_provider, start_date, snapshot
        )
        await assert_no_daily_stat_persisted(garmin_daily_stat_persistence_provider, failing_date)
        await assert_daily_stat_persisted(
            garmin_daily_stat_persistence_provider, end_date, snapshot
        )

    async def test_batch_upsert_garmin_daily_stats_should_return_409_when_no_session_has_been_established(  # noqa: E501
        self, api_client, mocker
    ):
        # given
        fetch_daily_snapshot = spy_on_fetch_daily_snapshot(mocker)

        # when
        response = await batch_upsert_garmin_daily_stats(
            api_client, date(2026, 8, 20), date(2026, 8, 22)
        )

        # then
        assert_response_status(response, 409)
        fetch_daily_snapshot.assert_not_called()

    async def test_batch_upsert_garmin_daily_stats_should_overwrite_existing_row_when_date_already_stored(  # noqa: E501
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        start_date = date(2026, 8, 20)
        stored_date = date(2026, 8, 21)
        end_date = date(2026, 8, 22)
        snapshot = GarminDailySnapshot(
            steps=8500,
            resting_heart_rate=52,
            sleep_seconds=25200,
            peak_body_battery=68,
            sleep_score=85,
            hrv_last_night_average=45,
            hrv_status="BALANCED",
            training_readiness_score=72,
            training_status="PRODUCTIVE",
            vo2_max=45,
            fitness_age=32.5,
            weight_grams=70500,
            intensity_minutes=35,
        )
        snapshots = {start_date: snapshot, stored_date: snapshot, end_date: snapshot}
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        await a_daily_stat_is_already_stored(garmin_daily_stat_persistence_provider, stored_date)
        garmin_returns_daily_stats(mocker, snapshots)

        # when
        response = await batch_upsert_garmin_daily_stats(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        assert response.json()["failedDates"] == []
        await assert_daily_stat_persisted(
            garmin_daily_stat_persistence_provider, stored_date, snapshot
        )
