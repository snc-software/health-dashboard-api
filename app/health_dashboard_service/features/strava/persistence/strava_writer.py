from ....infrastructure.postgres.persistence_controller import PersistenceController
from .strava_entities import StravaToken


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
