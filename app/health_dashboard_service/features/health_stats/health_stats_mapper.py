"""Mapping between the Garmin persistence row and the health_stats domain/contract types."""

from ...contracts.health_stats import DailyHealthStatResponse
from ..garmin.persistence.garmin_entities import GarminDailyStat
from .domain.health_stats_models import DailyHealthStatModel


def map_from_persistence_to_domain_daily_health_stat(stat: GarminDailyStat) -> DailyHealthStatModel:
    """Map from persistence GarminDailyStat to domain DailyHealthStatModel"""
    return DailyHealthStatModel(
        stat_date=stat.StatDate,
        steps=stat.Steps,
        resting_heart_rate=stat.RestingHeartRate,
        sleep_seconds=stat.SleepSeconds,
        sleep_score=stat.SleepScore,
        peak_body_battery=stat.PeakBodyBattery,
        hrv_last_night_average=stat.HrvLastNightAverage,
        hrv_status=stat.HrvStatus,
        training_readiness_score=stat.TrainingReadinessScore,
        training_status=stat.TrainingStatus,
        vo2_max=stat.Vo2Max,
        fitness_age=stat.FitnessAge,
        weight_grams=stat.WeightGrams,
        intensity_minutes=stat.IntensityMinutes,
        updated_timestamp=stat.UpdatedTimestamp,
    )


def map_from_domain_to_response_daily_health_stat(
    stat_model: DailyHealthStatModel,
) -> DailyHealthStatResponse:
    """Map from domain DailyHealthStatModel to response contract DailyHealthStatResponse"""
    return DailyHealthStatResponse(
        date=stat_model.stat_date,
        steps=stat_model.steps,
        resting_heart_rate=stat_model.resting_heart_rate,
        sleep_seconds=stat_model.sleep_seconds,
        sleep_score=stat_model.sleep_score,
        peak_body_battery=stat_model.peak_body_battery,
        hrv_last_night_average=stat_model.hrv_last_night_average,
        hrv_status=stat_model.hrv_status,
        training_readiness_score=stat_model.training_readiness_score,
        training_status=stat_model.training_status,
        vo2_max=stat_model.vo2_max,
        fitness_age=stat_model.fitness_age,
        weight_grams=stat_model.weight_grams,
        intensity_minutes=stat_model.intensity_minutes,
        updated_timestamp=stat_model.updated_timestamp,
    )
