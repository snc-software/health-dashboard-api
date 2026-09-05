from datetime import date

import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.strava import (
    FetchStravaActivitiesRequest,
    FetchStravaActivitiesResponse,
    GetStravaActivitiesRequest,
    GetStravaActivitySummaryRequest,
    StravaActivityResponse,
    StravaActivitySummaryResponse,
    StravaSessionResponse,
)
from tests.builders.strava_builders import StravaAutoFixture


class StravaContractTests:
    def test_strava_session_response_should_serialise_as_camel_case(self):
        response = StravaAutoFixture.generate(StravaSessionResponse)

        payload = response.model_dump(by_alias=True)

        assert "athleteId" in payload
        assert "updatedTimestamp" in payload

    def test_fetch_strava_activities_request_should_reject_when_end_date_is_before_start_date(self):
        with pytest.raises(ValidationError):
            FetchStravaActivitiesRequest(start_date=date(2026, 8, 20), end_date=date(2026, 8, 19))

    def test_fetch_strava_activities_request_should_accept_when_end_date_equals_start_date(self):
        request = FetchStravaActivitiesRequest(
            start_date=date(2026, 8, 20), end_date=date(2026, 8, 20)
        )

        assert request.start_date == request.end_date == date(2026, 8, 20)

    def test_get_strava_activities_request_should_reject_when_end_date_is_before_start_date(self):
        with pytest.raises(ValidationError):
            GetStravaActivitiesRequest(start_date=date(2026, 8, 20), end_date=date(2026, 8, 19))

    def test_get_strava_activity_summary_request_should_reject_when_end_date_is_before_start_date(
        self,
    ):
        with pytest.raises(ValidationError):
            GetStravaActivitySummaryRequest(
                start_date=date(2026, 8, 20), end_date=date(2026, 8, 19)
            )

    def test_fetch_strava_activities_response_should_serialise_as_camel_case(self):
        response = StravaAutoFixture.generate(FetchStravaActivitiesResponse)

        payload = response.model_dump(by_alias=True)

        assert "countsByType" in payload

    def test_strava_activity_response_should_serialise_as_camel_case(self):
        response = StravaAutoFixture.generate(StravaActivityResponse)

        payload = response.model_dump(by_alias=True)

        assert "stravaActivityId" in payload
        assert "sportType" in payload
        assert "startDate" in payload
        assert "startDateLocal" in payload
        assert "distanceMetres" in payload
        assert "movingTimeSeconds" in payload
        assert "elapsedTimeSeconds" in payload
        assert "totalElevationGainMetres" in payload
        assert "averageHeartrate" in payload
        assert "maxHeartrate" in payload
        assert "gearId" in payload

    def test_strava_activity_summary_response_should_serialise_as_camel_case(self):
        response = StravaAutoFixture.generate(StravaActivitySummaryResponse)

        payload = response.model_dump(by_alias=True)

        assert "currentPeriod" in payload
        assert "priorPeriod" in payload
        assert "totalActivities" in payload["currentPeriod"]
        assert "totalRunDistanceMetres" in payload["currentPeriod"]
        assert "averageRunPaceSecondsPerKm" in payload["currentPeriod"]
