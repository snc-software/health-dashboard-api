"""Test-only helper for seeding and reading GarminDailyStat rows directly against Postgres."""

from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from health_dashboard_service.features.garmin.persistence.garmin_entities import GarminDailyStat


class GarminDailyStatPersistenceProvider:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def insert(self, stat: GarminDailyStat) -> None:
        sql = text(
            """
            INSERT INTO public."GarminDailyStats"
                ("Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "PeakBodyBattery",
                 "SleepScore", "HrvLastNightAverage", "HrvStatus", "TrainingReadinessScore",
                 "TrainingStatus", "Spo2Average", "Vo2Max", "FitnessAge", "WeightGrams",
                 "IntensityMinutes", "UpdatedTimestamp")
            VALUES (:id, :stat_date, :steps, :resting_heart_rate, :sleep_seconds,
                    :peak_body_battery, :sleep_score, :hrv_last_night_average, :hrv_status,
                    :training_readiness_score, :training_status, :spo2_average, :vo2_max,
                    :fitness_age, :weight_grams, :intensity_minutes, :updated_timestamp)
            ON CONFLICT ("StatDate") DO UPDATE SET
                "Steps" = EXCLUDED."Steps",
                "RestingHeartRate" = EXCLUDED."RestingHeartRate",
                "SleepSeconds" = EXCLUDED."SleepSeconds",
                "PeakBodyBattery" = EXCLUDED."PeakBodyBattery",
                "SleepScore" = EXCLUDED."SleepScore",
                "HrvLastNightAverage" = EXCLUDED."HrvLastNightAverage",
                "HrvStatus" = EXCLUDED."HrvStatus",
                "TrainingReadinessScore" = EXCLUDED."TrainingReadinessScore",
                "TrainingStatus" = EXCLUDED."TrainingStatus",
                "Spo2Average" = EXCLUDED."Spo2Average",
                "Vo2Max" = EXCLUDED."Vo2Max",
                "FitnessAge" = EXCLUDED."FitnessAge",
                "WeightGrams" = EXCLUDED."WeightGrams",
                "IntensityMinutes" = EXCLUDED."IntensityMinutes",
                "UpdatedTimestamp" = EXCLUDED."UpdatedTimestamp"
            """
        )
        async with self._engine.begin() as connection:
            await connection.execute(
                sql,
                {
                    "id": stat.Id,
                    "stat_date": stat.StatDate,
                    "steps": stat.Steps,
                    "resting_heart_rate": stat.RestingHeartRate,
                    "sleep_seconds": stat.SleepSeconds,
                    "peak_body_battery": stat.PeakBodyBattery,
                    "sleep_score": stat.SleepScore,
                    "hrv_last_night_average": stat.HrvLastNightAverage,
                    "hrv_status": stat.HrvStatus,
                    "training_readiness_score": stat.TrainingReadinessScore,
                    "training_status": stat.TrainingStatus,
                    "spo2_average": stat.Spo2Average,
                    "vo2_max": stat.Vo2Max,
                    "fitness_age": stat.FitnessAge,
                    "weight_grams": stat.WeightGrams,
                    "intensity_minutes": stat.IntensityMinutes,
                    "updated_timestamp": stat.UpdatedTimestamp,
                },
            )

    async def get_by_date(self, stat_date: date) -> GarminDailyStat | None:
        sql = text(
            """
            SELECT "Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "PeakBodyBattery",
                   "SleepScore", "HrvLastNightAverage", "HrvStatus", "TrainingReadinessScore",
                   "TrainingStatus", "Spo2Average", "Vo2Max", "FitnessAge", "WeightGrams",
                   "IntensityMinutes", "UpdatedTimestamp"
            FROM public."GarminDailyStats"
            WHERE "StatDate" = :stat_date
            """
        )
        async with self._engine.connect() as connection:
            result = await connection.execute(sql, {"stat_date": stat_date})
            row = result.mappings().first()
            return GarminDailyStat(**row) if row else None
