import health_dashboard_service.features.garmin.garmin_mapper as mapper
from health_dashboard_service.contracts.garmin import AuthenticateGarminRequest
from health_dashboard_service.features.garmin.domain.garmin_models import (
    GarminDailyStatModel,
    GarminTokenModel,
)
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GarminDailyStat,
    GarminToken,
)
from tests.builders.garmin_builders import GarminAutoFixture


class GarminMapperTests:
    def test_contract_to_domain_credentials_should_carry_email_and_password_unchanged(self):
        request = GarminAutoFixture.generate(AuthenticateGarminRequest)

        result = mapper.map_from_contract_to_domain_credentials(request)

        assert result.email == request.email
        assert result.password == request.password

    def test_persistence_to_domain_token_should_copy_every_field(self):
        token = GarminAutoFixture.generate(GarminToken)

        result = mapper.map_from_persistence_to_domain_token(token)

        assert result.id == token.Id
        assert result.token_data == token.TokenData
        assert result.created_timestamp == token.CreatedTimestamp
        assert result.updated_timestamp == token.UpdatedTimestamp

    def test_domain_to_persistence_token_should_copy_every_field(self):
        token_model = GarminAutoFixture.generate(GarminTokenModel)

        result = mapper.map_from_domain_to_persistence_token(token_model)

        assert result.Id == token_model.id
        assert result.TokenData == token_model.token_data
        assert result.CreatedTimestamp == token_model.created_timestamp
        assert result.UpdatedTimestamp == token_model.updated_timestamp

    def test_persistence_to_domain_daily_stat_should_copy_every_field(self):
        stat = GarminAutoFixture.generate(GarminDailyStat)

        result = mapper.map_from_persistence_to_domain_daily_stat(stat)

        assert result.id == stat.Id
        assert result.stat_date == stat.StatDate
        assert result.steps == stat.Steps
        assert result.resting_heart_rate == stat.RestingHeartRate
        assert result.sleep_seconds == stat.SleepSeconds
        assert result.body_battery == stat.BodyBattery
        assert result.updated_timestamp == stat.UpdatedTimestamp

    def test_domain_to_persistence_daily_stat_should_copy_every_field(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_persistence_daily_stat(stat_model)

        assert result.Id == stat_model.id
        assert result.StatDate == stat_model.stat_date
        assert result.Steps == stat_model.steps
        assert result.RestingHeartRate == stat_model.resting_heart_rate
        assert result.SleepSeconds == stat_model.sleep_seconds
        assert result.BodyBattery == stat_model.body_battery
        assert result.UpdatedTimestamp == stat_model.updated_timestamp

    def test_domain_to_response_daily_stat_should_copy_every_field(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_response_daily_stat(stat_model)

        assert result.stat_date == stat_model.stat_date
        assert result.steps == stat_model.steps
        assert result.resting_heart_rate == stat_model.resting_heart_rate
        assert result.sleep_seconds == stat_model.sleep_seconds
        assert result.body_battery == stat_model.body_battery
        assert result.updated_timestamp == stat_model.updated_timestamp

    def test_domain_to_response_daily_stat_should_serialise_as_camel_case(self):
        stat_model = GarminAutoFixture.generate(GarminDailyStatModel)

        result = mapper.map_from_domain_to_response_daily_stat(stat_model)
        payload = result.model_dump(by_alias=True)

        assert "statDate" in payload
        assert "restingHeartRate" in payload
        assert "sleepSeconds" in payload
        assert "bodyBattery" in payload
        assert "updatedTimestamp" in payload
