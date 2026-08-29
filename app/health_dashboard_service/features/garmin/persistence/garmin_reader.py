from datetime import date

from ....infrastructure.postgres.persistence_controller import PersistenceController
from .garmin_entities import GARMIN_TOKEN_SINGLETON_ID, GarminDailyStat, GarminToken


async def get_token(pc: PersistenceController) -> GarminToken | None:
    row = await pc.query_single_or_default(
        """
        SELECT "Id", "TokenData", "CreatedTimestamp", "UpdatedTimestamp"
        FROM public."GarminTokens"
        WHERE "Id" = :id
        """,
        {"id": GARMIN_TOKEN_SINGLETON_ID},
    )
    return GarminToken(**row) if row else None


async def get_daily_stat_by_date(
    pc: PersistenceController, stat_date: date
) -> GarminDailyStat | None:
    row = await pc.query_single_or_default(
        """
        SELECT "Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "BodyBattery",
               "UpdatedTimestamp"
        FROM public."GarminDailyStats"
        WHERE "StatDate" = :stat_date
        """,
        {"stat_date": stat_date},
    )
    return GarminDailyStat(**row) if row else None
