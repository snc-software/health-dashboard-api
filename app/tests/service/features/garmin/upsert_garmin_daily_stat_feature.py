"""Service tests for POST /garmin-daily-stats."""

from datetime import date

from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminDailySnapshot,
)

from .upsert_garmin_daily_stat_steps import (
    a_garmin_session_has_been_established,
    assert_daily_stat_persisted,
    assert_response_status,
    garmin_is_unreachable,
    garmin_returns_daily_stats,
    upsert_garmin_daily_stat,
)


class TestUpsertGarminDailyStatFeature:
    async def test_upsert_garmin_daily_stat_should_persist_and_return_daily_stats(
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        stat_date = date(2026, 8, 20)
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
            spo2_average=97,
            vo2_max=45,
            fitness_age=32.5,
            weight_grams=70500,
            intensity_minutes=35,
        )
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_returns_daily_stats(mocker, snapshot)

        # when
        response = await upsert_garmin_daily_stat(api_client, stat_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert body["steps"] == snapshot.steps
        assert body["restingHeartRate"] == snapshot.resting_heart_rate
        assert body["peakBodyBattery"] == snapshot.peak_body_battery
        assert body["sleepScore"] == snapshot.sleep_score
        assert body["hrvLastNightAverage"] == snapshot.hrv_last_night_average
        assert body["hrvStatus"] == snapshot.hrv_status
        assert body["trainingReadinessScore"] == snapshot.training_readiness_score
        assert body["trainingStatus"] == snapshot.training_status
        assert body["spo2Average"] == snapshot.spo2_average
        assert body["vo2Max"] == snapshot.vo2_max
        assert body["fitnessAge"] == snapshot.fitness_age
        assert body["weightGrams"] == snapshot.weight_grams
        assert body["intensityMinutes"] == snapshot.intensity_minutes
        await assert_daily_stat_persisted(
            garmin_daily_stat_persistence_provider, stat_date, snapshot
        )

    async def test_upsert_garmin_daily_stat_should_return_409_when_no_session_has_been_established(
        self, api_client
    ):
        # when
        response = await upsert_garmin_daily_stat(api_client, date(2026, 8, 20))

        # then
        assert_response_status(response, 409)

    async def test_upsert_garmin_daily_stat_should_return_502_when_garmin_is_unreachable(
        self, api_client, mocker, garmin_token_persistence_provider
    ):
        # given
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_is_unreachable(mocker)

        # when
        response = await upsert_garmin_daily_stat(api_client, date(2026, 8, 20))

        # then
        assert_response_status(response, 502)
