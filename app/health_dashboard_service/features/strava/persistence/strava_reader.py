from datetime import date

from ....infrastructure.postgres.persistence_controller import PersistenceController
from .strava_entities import (
    STRAVA_TOKEN_SINGLETON_ID,
    StravaActivity,
    StravaActivityStatsRow,
    StravaToken,
)


async def get_token(pc: PersistenceController) -> StravaToken | None:
    row = await pc.query_single_or_default(
        """
        SELECT "Id", "AccessToken", "RefreshToken", "ExpiresAt", "AthleteId", "Scope",
               "CreatedTimestamp", "UpdatedTimestamp"
        FROM public."StravaTokens"
        WHERE "Id" = :id
        """,
        {"id": STRAVA_TOKEN_SINGLETON_ID},
    )
    return StravaToken(**row) if row else None


async def get_activities_in_range(
    pc: PersistenceController, start_date: date, end_date: date
) -> list[StravaActivity]:
    rows = await pc.query(
        """
        SELECT "Id", "StravaActivityId", "Name", "SportType", "StartDate",
               "StartDateLocal", "DistanceMetres", "MovingTimeSeconds", "ElapsedTimeSeconds",
               "TotalElevationGainMetres", "AverageHeartrate", "MaxHeartrate", "GearId",
               "UpdatedTimestamp"
        FROM public."StravaActivities"
        WHERE "StartDateLocal"::date BETWEEN :start_date AND :end_date
        ORDER BY "StartDateLocal" ASC
        """,
        {"start_date": start_date, "end_date": end_date},
    )
    return [StravaActivity(**row) for row in rows]


async def get_activity_stats_in_range(
    pc: PersistenceController, start_date: date, end_date: date
) -> StravaActivityStatsRow:
    row = await pc.query_single(
        """
        SELECT
            COUNT(*) AS "TotalActivities",
            COALESCE(SUM("DistanceMetres") FILTER (WHERE "SportType" = 'Run'), 0)
                AS "TotalRunDistanceMetres",
            COALESCE(SUM("MovingTimeSeconds") FILTER (WHERE "SportType" = 'Run'), 0)
                AS "TotalRunMovingTimeSeconds"
        FROM public."StravaActivities"
        WHERE "StartDateLocal"::date BETWEEN :start_date AND :end_date
        """,
        {"start_date": start_date, "end_date": end_date},
    )
    return StravaActivityStatsRow(**row)
