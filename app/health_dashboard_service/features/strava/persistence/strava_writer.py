from ....infrastructure.postgres.persistence_controller import PersistenceController
from .strava_entities import StravaActivity, StravaToken


async def upsert_token(pc: PersistenceController, token: StravaToken) -> StravaToken:
    row = await pc.execute_with_result(
        """
        INSERT INTO public."StravaTokens"
            ("Id", "AccessToken", "RefreshToken", "ExpiresAt", "AthleteId", "Scope",
             "CreatedTimestamp", "UpdatedTimestamp")
        VALUES (:id, :access_token, :refresh_token, :expires_at, :athlete_id, :scope,
                :created_timestamp, :updated_timestamp)
        ON CONFLICT ("Id") DO UPDATE SET
            "AccessToken" = EXCLUDED."AccessToken",
            "RefreshToken" = EXCLUDED."RefreshToken",
            "ExpiresAt" = EXCLUDED."ExpiresAt",
            "AthleteId" = EXCLUDED."AthleteId",
            "Scope" = EXCLUDED."Scope",
            "UpdatedTimestamp" = EXCLUDED."UpdatedTimestamp"
        RETURNING "Id", "AccessToken", "RefreshToken", "ExpiresAt", "AthleteId", "Scope",
                  "CreatedTimestamp", "UpdatedTimestamp"
        """,
        {
            "id": token.Id,
            "access_token": token.AccessToken,
            "refresh_token": token.RefreshToken,
            "expires_at": token.ExpiresAt,
            "athlete_id": token.AthleteId,
            "scope": token.Scope,
            "created_timestamp": token.CreatedTimestamp,
            "updated_timestamp": token.UpdatedTimestamp,
        },
    )
    return StravaToken(**row)


async def upsert_activities(
    pc: PersistenceController, activities: list[StravaActivity]
) -> list[StravaActivity]:
    saved: list[StravaActivity] = []
    for activity in activities:
        row = await pc.execute_with_result(
            """
            INSERT INTO public."StravaActivities"
                ("Id", "StravaActivityId", "Name", "SportType", "StartDate",
                 "StartDateLocal", "DistanceMetres", "MovingTimeSeconds", "ElapsedTimeSeconds",
                 "TotalElevationGainMetres", "AverageHeartrate", "MaxHeartrate", "GearId",
                 "UpdatedTimestamp")
            VALUES (:id, :strava_activity_id, :name, :sport_type, :start_date,
                    :start_date_local, :distance_metres, :moving_time_seconds,
                    :elapsed_time_seconds, :total_elevation_gain_metres, :average_heartrate,
                    :max_heartrate, :gear_id, :updated_timestamp)
            ON CONFLICT ("StravaActivityId") DO UPDATE SET
                "Name" = EXCLUDED."Name",
                "SportType" = EXCLUDED."SportType",
                "StartDate" = EXCLUDED."StartDate",
                "StartDateLocal" = EXCLUDED."StartDateLocal",
                "DistanceMetres" = EXCLUDED."DistanceMetres",
                "MovingTimeSeconds" = EXCLUDED."MovingTimeSeconds",
                "ElapsedTimeSeconds" = EXCLUDED."ElapsedTimeSeconds",
                "TotalElevationGainMetres" = EXCLUDED."TotalElevationGainMetres",
                "AverageHeartrate" = EXCLUDED."AverageHeartrate",
                "MaxHeartrate" = EXCLUDED."MaxHeartrate",
                "GearId" = EXCLUDED."GearId",
                "UpdatedTimestamp" = EXCLUDED."UpdatedTimestamp"
            RETURNING "Id", "StravaActivityId", "Name", "SportType", "StartDate",
                      "StartDateLocal", "DistanceMetres", "MovingTimeSeconds",
                      "ElapsedTimeSeconds", "TotalElevationGainMetres", "AverageHeartrate",
                      "MaxHeartrate", "GearId", "UpdatedTimestamp"
            """,
            {
                "id": activity.Id,
                "strava_activity_id": activity.StravaActivityId,
                "name": activity.Name,
                "sport_type": activity.SportType,
                "start_date": activity.StartDate,
                "start_date_local": activity.StartDateLocal,
                "distance_metres": activity.DistanceMetres,
                "moving_time_seconds": activity.MovingTimeSeconds,
                "elapsed_time_seconds": activity.ElapsedTimeSeconds,
                "total_elevation_gain_metres": activity.TotalElevationGainMetres,
                "average_heartrate": activity.AverageHeartrate,
                "max_heartrate": activity.MaxHeartrate,
                "gear_id": activity.GearId,
                "updated_timestamp": activity.UpdatedTimestamp,
            },
        )
        saved.append(StravaActivity(**row))
    return saved
