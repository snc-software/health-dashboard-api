import uuid
from datetime import date

import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    BatchUpsertGarminDailyStatsRequest,
    BatchUpsertGarminDailyStatsResponse,
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

    def test_batch_upsert_request_should_reject_when_end_date_is_before_start_date(self):
        with pytest.raises(ValidationError):
            BatchUpsertGarminDailyStatsRequest(
                start_date=date(2026, 8, 20), end_date=date(2026, 8, 19)
            )

    def test_batch_upsert_request_should_accept_when_end_date_equals_start_date(self):
        request = BatchUpsertGarminDailyStatsRequest(
            start_date=date(2026, 8, 20), end_date=date(2026, 8, 20)
        )

        assert request.start_date == request.end_date == date(2026, 8, 20)

    def test_batch_upsert_response_should_serialise_as_camel_case(self):
        response = GarminAutoFixture.generate(BatchUpsertGarminDailyStatsResponse)

        payload = response.model_dump(by_alias=True)

        assert "failedDates" in payload

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
