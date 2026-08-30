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
            ("Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "PeakBodyBattery",
             "SleepScore", "HrvLastNightAverage", "HrvStatus", "TrainingReadinessScore",
             "TrainingStatus", "Spo2Average", "Vo2Max", "FitnessAge", "WeightGrams",
             "IntensityMinutes", "UpdatedTimestamp")
        VALUES (:id, :stat_date, :steps, :resting_heart_rate, :sleep_seconds, :peak_body_battery,
                :sleep_score, :hrv_last_night_average, :hrv_status, :training_readiness_score,
                :training_status, :spo2_average, :vo2_max, :fitness_age, :weight_grams,
                :intensity_minutes, :updated_timestamp)
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
        RETURNING "Id", "StatDate", "Steps", "RestingHeartRate", "SleepSeconds", "PeakBodyBattery",
                  "SleepScore", "HrvLastNightAverage", "HrvStatus", "TrainingReadinessScore",
                  "TrainingStatus", "Spo2Average", "Vo2Max", "FitnessAge", "WeightGrams",
                  "IntensityMinutes", "UpdatedTimestamp"
        """,
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
    return GarminDailyStat(**row)
