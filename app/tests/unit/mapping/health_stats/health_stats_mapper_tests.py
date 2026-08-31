import health_dashboard_service.features.health_stats.health_stats_mapper as mapper
from health_dashboard_service.features.garmin.persistence.garmin_entities import GarminDailyStat
from health_dashboard_service.features.health_stats.domain.health_stats_models import (
    DailyHealthStatModel,
)
from tests.builders.garmin_builders import GarminAutoFixture
from tests.builders.health_stats_builders import HealthStatsAutoFixture


class HealthStatsMapperTests:
    def test_can_map_from_persistence_GarminDailyStat_to_domain_DailyHealthStatModel(self):
        stat = GarminAutoFixture.generate(GarminDailyStat)

        result = mapper.map_from_persistence_to_domain_daily_health_stat(stat)

        assert result.stat_date == stat.StatDate
        assert result.steps == stat.Steps
        assert result.resting_heart_rate == stat.RestingHeartRate
        assert result.sleep_seconds == stat.SleepSeconds
        assert result.sleep_score == stat.SleepScore
        assert result.peak_body_battery == stat.PeakBodyBattery
        assert result.hrv_last_night_average == stat.HrvLastNightAverage
        assert result.hrv_status == stat.HrvStatus
        assert result.training_readiness_score == stat.TrainingReadinessScore
        assert result.training_status == stat.TrainingStatus
        assert result.vo2_max == stat.Vo2Max
        assert result.fitness_age == stat.FitnessAge
        assert result.weight_grams == stat.WeightGrams
        assert result.intensity_minutes == stat.IntensityMinutes
        assert result.updated_timestamp == stat.UpdatedTimestamp

    def test_can_map_from_domain_DailyHealthStatModel_to_response_DailyHealthStatResponse(self):
        stat_model = HealthStatsAutoFixture.generate(DailyHealthStatModel)

        result = mapper.map_from_domain_to_response_daily_health_stat(stat_model)

        assert result.date == stat_model.stat_date
        assert result.steps == stat_model.steps
        assert result.resting_heart_rate == stat_model.resting_heart_rate
        assert result.sleep_seconds == stat_model.sleep_seconds
        assert result.sleep_score == stat_model.sleep_score
        assert result.peak_body_battery == stat_model.peak_body_battery
        assert result.hrv_last_night_average == stat_model.hrv_last_night_average
        assert result.hrv_status == stat_model.hrv_status
        assert result.training_readiness_score == stat_model.training_readiness_score
        assert result.training_status == stat_model.training_status
        assert result.vo2_max == stat_model.vo2_max
        assert result.fitness_age == stat_model.fitness_age
        assert result.weight_grams == stat_model.weight_grams
        assert result.intensity_minutes == stat_model.intensity_minutes
        assert result.updated_timestamp == stat_model.updated_timestamp
