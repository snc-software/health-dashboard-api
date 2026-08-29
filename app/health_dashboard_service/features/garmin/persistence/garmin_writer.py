from ....infrastructure.postgres.persistence_controller import PersistenceController
from .garmin_entities import GarminDailyStat, GarminToken


async def upsert_token(pc: PersistenceController, token: GarminToken) -> GarminToken:
    row = await pc.execute_with_result(
        """
        INSERT INTO public."GarminTokens"
            ("Id", "TokenData", "CreatedTimestamp", "UpdatedTimestamp")
        VALUES (:id, :token_data, :created_timestamp, :updated_timestamp)
        ON CONFLICT ("Id") DO UPDATE SET
            "TokenData" = EXCLUDED."TokenData",
            "UpdatedTimestamp" = EXCLUDED."UpdatedTimestamp"
        RETURNING "Id", "TokenData", "CreatedTimestamp", "UpdatedTimestamp"
        """,
        {
            "id": token.Id,
            "token_data": token.TokenData,
            "created_timestamp": token.CreatedTimestamp,
            "updated_timestamp": token.UpdatedTimestamp,
        },
    )
    return GarminToken(**row)


async def upsert_daily_stat(pc: PersistenceController, stat: GarminDailyStat) -> GarminDailyStat:
    row = await pc.execute_with_result(
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
        RETURNING "Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "BodyBattery",
                  "UpdatedTimestamp"
        """,
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
    return GarminDailyStat(**row)
