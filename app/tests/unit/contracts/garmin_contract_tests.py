import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    GarminDailyStatResponse,
)
from tests.builders.garmin_builders import GarminAutoFixture


class GarminContractTests:
    def test_authenticate_request_should_reject_when_email_is_invalid(self):
        with pytest.raises(ValidationError):
            AuthenticateGarminRequest(email="not-an-email", password="hunter2")

    def test_authenticate_request_should_reject_when_password_is_empty(self):
        with pytest.raises(ValidationError):
            AuthenticateGarminRequest(email="athlete@example.com", password="")

    def test_daily_stat_response_should_serialise_as_camel_case(self):
        response = GarminAutoFixture.generate(GarminDailyStatResponse)

        payload = response.model_dump(by_alias=True)

        assert "statDate" in payload
        assert "restingHeartRate" in payload
        assert "sleepSeconds" in payload
        assert "bodyBattery" in payload
        assert "updatedTimestamp" in payload
