"""Service tests for POST /garmin/refresh."""

from datetime import UTC, date, datetime

from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminDailySnapshot,
)

from .refresh_garmin_data_steps import (
    a_garmin_session_has_been_established,
    assert_daily_stat_persisted,
    assert_response_status,
    garmin_is_unreachable,
    garmin_returns_daily_stats,
    refresh_garmin_data,
)


class TestRefreshGarminDataFeature:
    async def test_refresh_garmin_data_should_persist_and_return_daily_stats_when_session_exists(
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
        response = await refresh_garmin_data(api_client, stat_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert body["steps"] == snapshot.steps
        assert body["restingHeartRate"] == snapshot.resting_heart_rate
        await assert_daily_stat_persisted(
            garmin_daily_stat_persistence_provider, stat_date, snapshot
        )

    async def test_refresh_garmin_data_should_return_409_when_no_session_has_been_established(
        self, api_client
    ):
        # when
        response = await refresh_garmin_data(api_client)

        # then
        assert_response_status(response, 409)

    async def test_refresh_garmin_data_should_return_502_when_garmin_is_unreachable(
        self, api_client, mocker, garmin_token_persistence_provider
    ):
        # given
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_is_unreachable(mocker)

        # when
        response = await refresh_garmin_data(api_client)

        # then
        assert_response_status(response, 502)

    async def test_refresh_garmin_data_should_default_to_todays_date_when_no_date_is_supplied(
        self,
        api_client,
        mocker,
        garmin_token_persistence_provider,
        garmin_daily_stat_persistence_provider,
    ):
        # given
        snapshot = GarminDailySnapshot(
            steps=1000, resting_heart_rate=60, sleep_seconds=None, body_battery=None
        )
        await a_garmin_session_has_been_established(garmin_token_persistence_provider)
        garmin_returns_daily_stats(mocker, snapshot)

        # when
        response = await refresh_garmin_data(api_client)

        # then
        assert_response_status(response, 200)
        assert response.json()["statDate"] == datetime.now(UTC).date().isoformat()
