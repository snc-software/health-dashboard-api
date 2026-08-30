import uuid

import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    GarminDailyStatResponse,
    SubmitGarminMfaRequest,
    UpsertGarminDailyStatRequest,
)
from tests.builders.garmin_builders import GarminAutoFixture


class GarminContractTests:
    def test_authenticate_request_should_reject_when_email_is_invalid(self):
        with pytest.raises(ValidationError):
            AuthenticateGarminRequest(email="not-an-email", password="hunter2")

    def test_authenticate_request_should_reject_when_password_is_empty(self):
        with pytest.raises(ValidationError):
            AuthenticateGarminRequest(email="athlete@example.com", password="")

    def test_submit_mfa_request_should_reject_when_code_is_empty(self):
        with pytest.raises(ValidationError):
            SubmitGarminMfaRequest(mfa_session_id=uuid.uuid4(), code="")

    def test_submit_mfa_request_should_reject_when_session_id_is_malformed(self):
        with pytest.raises(ValidationError):
            SubmitGarminMfaRequest(mfa_session_id="not-a-uuid", code="123456")

    def test_upsert_daily_stat_request_should_reject_when_stat_date_is_missing(self):
        with pytest.raises(ValidationError):
            UpsertGarminDailyStatRequest()

    def test_daily_stat_response_should_serialise_as_camel_case(self):
        response = GarminAutoFixture.generate(GarminDailyStatResponse)

        payload = response.model_dump(by_alias=True)

        assert "statDate" in payload
        assert "restingHeartRate" in payload
        assert "sleepSeconds" in payload
        assert "peakBodyBattery" in payload
        assert "sleepScore" in payload
        assert "hrvLastNightAverage" in payload
        assert "hrvStatus" in payload
        assert "trainingReadinessScore" in payload
        assert "trainingStatus" in payload
        assert "spo2Average" in payload
        assert "vo2Max" in payload
        assert "fitnessAge" in payload
        assert "weightGrams" in payload
        assert "intensityMinutes" in payload
        assert "updatedTimestamp" in payload
