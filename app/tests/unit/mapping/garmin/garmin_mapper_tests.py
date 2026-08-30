from datetime import date

import health_dashboard_service.features.garmin.garmin_mapper as mapper
from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    SubmitGarminMfaRequest,
)
from health_dashboard_service.features.garmin.domain.garmin_models import (
    GarminAuthenticationResultModel,
    GarminDailyStatModel,
    GarminTokenModel,
)
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GarminDailyStat,
    GarminToken,
)
from tests.builders.garmin_builders import GarminAutoFixture


class GarminMapperTests:
    def test_can_map_from_contract_AuthenticateGarminRequest_to_domain_GarminCredentialsModel(self):
        request = GarminAutoFixture.generate(AuthenticateGarminRequest)

        result = mapper.map_from_contract_to_domain_credentials(request)

        assert result.email == request.email
        assert result.password == request.password

    def test_can_map_from_persistence_GarminToken_to_domain_GarminTokenModel(self):
        token = GarminAutoFixture.generate(GarminToken)

        result = mapper.map_from_persistence_to_domain_token(token)

        assert result.id == token.Id
        assert result.token_data == token.TokenData
        assert result.created_timestamp == token.CreatedTimestamp
        assert result.updated_timestamp == token.UpdatedTimestamp

    def test_can_map_from_domain_GarminTokenModel_to_persistence_GarminToken(self):
        token_model = GarminAutoFixture.generate(GarminTokenModel)

        result = mapper.map_from_domain_to_persistence_token(token_model)

        assert result.Id == token_model.id
        assert result.TokenData == token_model.token_data
        assert result.CreatedTimestamp == token_model.created_timestamp
        assert result.UpdatedTimestamp == token_model.updated_timestamp

    def test_can_map_from_persistence_GarminDailyStat_to_domain_GarminDailyStatModel(self):
        stat = GarminAutoFixture.generate(GarminDailyStat)

        result = mapper.map_from_persistence_to_domain_daily_stat(stat)

        assert result.id == stat.Id
        assert result.stat_date == stat.StatDate
        assert result.steps == stat.Steps
        assert result.resting_heart_rate == stat.RestingHeartRate
        assert result.sleep_seconds == stat.SleepSeconds
        assert result.peak_body_battery == stat.PeakBodyBattery
        assert result.sleep_score == stat.SleepScore
        assert result.hrv_last_night_average == stat.HrvLastNightAverage
        assert result.hrv_status == stat.HrvStatus
        assert result.training_readiness_score == stat.TrainingReadinessScore
        assert result.training_status == stat.TrainingStatus
        assert result.spo2_average == stat.Spo2Average
        assert result.vo2_max == stat.Vo2Max
        assert result.fitness_age == stat.FitnessAge
        assert result.weight_grams == stat.WeightGrams
        assert result.intensity_minutes == stat.IntensityMinutes
        assert result.updated_timestamp == stat.UpdatedTimestamp

    def test_can_map_from_domain_GarminDailyStatModel_to_persistence_GarminDailyStat(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_persistence_daily_stat(stat_model)

        assert result.Id == stat_model.id
        assert result.StatDate == stat_model.stat_date
        assert result.Steps == stat_model.steps
        assert result.RestingHeartRate == stat_model.resting_heart_rate
        assert result.SleepSeconds == stat_model.sleep_seconds
        assert result.PeakBodyBattery == stat_model.peak_body_battery
        assert result.SleepScore == stat_model.sleep_score
        assert result.HrvLastNightAverage == stat_model.hrv_last_night_average
        assert result.HrvStatus == stat_model.hrv_status
        assert result.TrainingReadinessScore == stat_model.training_readiness_score
        assert result.TrainingStatus == stat_model.training_status
        assert result.Spo2Average == stat_model.spo2_average
        assert result.Vo2Max == stat_model.vo2_max
        assert result.FitnessAge == stat_model.fitness_age
        assert result.WeightGrams == stat_model.weight_grams
        assert result.IntensityMinutes == stat_model.intensity_minutes
        assert result.UpdatedTimestamp == stat_model.updated_timestamp

    def test_can_map_from_domain_GarminDailyStatModel_to_response_GarminDailyStatResponse(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_response_daily_stat(stat_model)

        assert result.stat_date == stat_model.stat_date
        assert result.steps == stat_model.steps
        assert result.resting_heart_rate == stat_model.resting_heart_rate
        assert result.sleep_seconds == stat_model.sleep_seconds
        assert result.peak_body_battery == stat_model.peak_body_battery
        assert result.sleep_score == stat_model.sleep_score
        assert result.hrv_last_night_average == stat_model.hrv_last_night_average
        assert result.hrv_status == stat_model.hrv_status
        assert result.training_readiness_score == stat_model.training_readiness_score
        assert result.training_status == stat_model.training_status
        assert result.spo2_average == stat_model.spo2_average
        assert result.vo2_max == stat_model.vo2_max
        assert result.fitness_age == stat_model.fitness_age
        assert result.weight_grams == stat_model.weight_grams
        assert result.intensity_minutes == stat_model.intensity_minutes
        assert result.updated_timestamp == stat_model.updated_timestamp

    def test_domain_to_response_daily_stat_should_serialise_as_camel_case(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_response_daily_stat(stat_model)
        payload = result.model_dump(by_alias=True)

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

    def test_can_map_from_domain_GarminAuthenticationResultModel_to_response_GarminAuthenticateResponse(  # noqa: E501
        self,
    ):
        result_model = GarminAutoFixture.generate(GarminAuthenticationResultModel)

        result = mapper.map_from_domain_to_response_authentication_result(result_model)

        assert result.status == result_model.status
        assert result.mfa_session_id == result_model.mfa_session_id

    def test_can_map_from_contract_SubmitGarminMfaRequest_to_domain_GarminMfaSubmissionModel(self):
        request = GarminAutoFixture.generate(SubmitGarminMfaRequest)

        result = mapper.map_from_contract_to_domain_mfa_submission(request)

        assert result.mfa_session_id == request.mfa_session_id
        assert result.code == request.code

    def test_can_map_from_domain_failed_dates_to_response_BatchUpsertGarminDailyStatsResponse(self):
        failed_dates = [date(2026, 8, 20), date(2026, 8, 22)]

        result = mapper.map_from_domain_to_response_batch_upsert_result(failed_dates)

        assert result.failed_dates == failed_dates

    def test_can_map_from_domain_no_failed_dates_to_response_BatchUpsertGarminDailyStatsResponse(
        self,
    ):
        result = mapper.map_from_domain_to_response_batch_upsert_result([])

        assert result.failed_dates == []
