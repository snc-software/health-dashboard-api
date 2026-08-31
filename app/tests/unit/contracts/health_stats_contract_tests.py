from datetime import date

import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.health_stats import (
    DailyHealthStatResponse,
    GetDailyHealthStatsRequest,
)
from tests.builders.health_stats_builders import HealthStatsAutoFixture


class HealthStatsContractTests:
    def test_get_daily_health_stats_request_should_reject_when_end_date_is_before_start_date(self):
        with pytest.raises(ValidationError):
            GetDailyHealthStatsRequest(start_date=date(2026, 8, 20), end_date=date(2026, 8, 19))

    def test_get_daily_health_stats_request_should_accept_when_end_date_equals_start_date(self):
        request = GetDailyHealthStatsRequest(
            start_date=date(2026, 8, 20), end_date=date(2026, 8, 20)
        )

        assert request.start_date == request.end_date == date(2026, 8, 20)

    def test_daily_health_stat_response_should_serialise_as_camel_case(self):
        response = HealthStatsAutoFixture.generate(DailyHealthStatResponse)

        payload = response.model_dump(by_alias=True)

        assert "date" in payload
        assert "restingHeartRate" in payload
        assert "sleepSeconds" in payload
        assert "sleepScore" in payload
        assert "peakBodyBattery" in payload
        assert "hrvLastNightAverage" in payload
        assert "hrvStatus" in payload
        assert "trainingReadinessScore" in payload
        assert "trainingStatus" in payload
        assert "vo2Max" in payload
        assert "fitnessAge" in payload
        assert "weightGrams" in payload
        assert "intensityMinutes" in payload
        assert "updatedTimestamp" in payload

    def test_route_path_and_response_schema_should_not_reference_garmin(self):
        from fastapi.routing import APIRoute

        from health_dashboard_service.routes.health_stats import router

        paths = [r.path for r in router.routes if isinstance(r, APIRoute)]
        assert "/start/{startDate}/end/{endDate}/health-stats" in paths
        assert all("garmin" not in path.lower() for path in paths)

        for field_name, field in DailyHealthStatResponse.model_fields.items():
            assert "garmin" not in field_name.lower()
            if field.alias:
                assert "garmin" not in field.alias.lower()
