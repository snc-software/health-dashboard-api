"""Service tests for GET /daily-health-stats."""

from datetime import date

from .get_daily_health_stats_steps import (
    a_daily_stat_is_stored,
    assert_response_status,
    get_daily_health_stats,
)


class TestGetDailyHealthStatsFeature:
    async def test_get_daily_health_stats_should_return_full_list_when_every_date_has_a_stored_row(
        self, api_client, garmin_daily_stat_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        middle_date = date(2026, 8, 21)
        end_date = date(2026, 8, 22)
        first = await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, start_date)
        middle = await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, middle_date)
        last = await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, end_date)

        # when
        response = await get_daily_health_stats(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert [row["date"] for row in body] == [
            start_date.isoformat(),
            middle_date.isoformat(),
            end_date.isoformat(),
        ]
        assert body[0]["steps"] == first.Steps
        assert body[1]["steps"] == middle.Steps
        assert body[2]["steps"] == last.Steps

    async def test_get_daily_health_stats_should_return_only_existing_dates_when_some_dates_are_missing(  # noqa: E501
        self, api_client, garmin_daily_stat_persistence_provider
    ):
        # given
        start_date = date(2026, 8, 20)
        missing_date = date(2026, 8, 21)
        end_date = date(2026, 8, 22)
        await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, start_date)
        await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, end_date)

        # when
        response = await get_daily_health_stats(api_client, start_date, end_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert [row["date"] for row in body] == [start_date.isoformat(), end_date.isoformat()]
        assert missing_date.isoformat() not in [row["date"] for row in body]

    async def test_get_daily_health_stats_should_return_empty_list_when_no_stored_data_exists(
        self, api_client
    ):
        # when
        response = await get_daily_health_stats(api_client, date(2026, 8, 20), date(2026, 8, 22))

        # then
        assert_response_status(response, 200)
        assert response.json() == []

    async def test_get_daily_health_stats_should_return_400_when_end_date_is_before_start_date(
        self, api_client
    ):
        # when
        response = await get_daily_health_stats(api_client, date(2026, 8, 22), date(2026, 8, 20))

        # then
        assert_response_status(response, 400)

    async def test_get_daily_health_stats_should_return_single_record_when_start_date_equals_end_date(  # noqa: E501
        self, api_client, garmin_daily_stat_persistence_provider
    ):
        # given
        single_date = date(2026, 8, 20)
        await a_daily_stat_is_stored(garmin_daily_stat_persistence_provider, single_date)

        # when
        response = await get_daily_health_stats(api_client, single_date, single_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert len(body) == 1
        assert body[0]["date"] == single_date.isoformat()

    async def test_get_daily_health_stats_should_return_empty_list_when_single_date_has_no_stored_row(  # noqa: E501
        self, api_client
    ):
        # when
        single_date = date(2026, 8, 20)
        response = await get_daily_health_stats(api_client, single_date, single_date)

        # then
        assert_response_status(response, 200)
        assert response.json() == []

    async def test_get_daily_health_stats_should_include_null_fields_when_stat_not_present_on_stored_day(  # noqa: E501
        self, api_client, garmin_daily_stat_persistence_provider
    ):
        # given
        stat_date = date(2026, 8, 20)
        await a_daily_stat_is_stored(
            garmin_daily_stat_persistence_provider,
            stat_date,
            Steps=None,
            RestingHeartRate=None,
            HrvStatus=None,
        )

        # when
        response = await get_daily_health_stats(api_client, stat_date, stat_date)

        # then
        assert_response_status(response, 200)
        body = response.json()
        assert len(body) == 1
        assert body[0]["steps"] is None
        assert body[0]["restingHeartRate"] is None
        assert body[0]["hrvStatus"] is None
