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
    async def test_upsert_garmin_daily_stat_should_persist_and_return_daily_stats_when_session_exists(
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        stat_date = date(2026, 8, 20)
        snapshot = GarminDailySnapshot(
            steps=8500, resting_heart_rate=52, sleep_seconds=25200, body_battery=68
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
