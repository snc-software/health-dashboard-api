from ....infrastructure.postgres.persistence_controller import PersistenceController
from .strava_entities import STRAVA_TOKEN_SINGLETON_ID, StravaToken


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
