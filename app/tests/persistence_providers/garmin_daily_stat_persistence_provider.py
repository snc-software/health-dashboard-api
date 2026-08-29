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
                ("Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "BodyBattery",
                 "UpdatedTimestamp")
            VALUES (:id, :stat_date, :steps, :resting_heart_rate, :sleep_seconds, :body_battery,
                    :updated_timestamp)
            ON CONFLICT ("StatDate") DO UPDATE SET
                "Steps" = EXCLUDED."Steps",
                "RestingHeartRate" = EXCLUDED."RestingHeartRate",
                "SleepSeconds" = EXCLUDED."SleepSeconds",
                "BodyBattery" = EXCLUDED."BodyBattery",
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
                    "body_battery": stat.BodyBattery,
                    "updated_timestamp": stat.UpdatedTimestamp,
                },
            )

    async def get_by_date(self, stat_date: date) -> GarminDailyStat | None:
        sql = text(
            """
            SELECT "Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "BodyBattery",
                   "UpdatedTimestamp"
            FROM public."GarminDailyStats"
            WHERE "StatDate" = :stat_date
            """
        )
        async with self._engine.connect() as connection:
            result = await connection.execute(sql, {"stat_date": stat_date})
            row = result.mappings().first()
            return GarminDailyStat(**row) if row else None
