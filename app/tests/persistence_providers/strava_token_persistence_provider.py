"""Test-only helper for seeding and reading StravaToken rows directly against Postgres."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from health_dashboard_service.features.strava.persistence.strava_entities import StravaToken


class StravaTokenPersistenceProvider:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def insert(self, token: StravaToken) -> None:
        sql = text(
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
            """
        )
        async with self._engine.begin() as connection:
            await connection.execute(
                sql,
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

    async def get_by_id(self, token_id: UUID) -> StravaToken | None:
        sql = text(
            """
            SELECT "Id", "AccessToken", "RefreshToken", "ExpiresAt", "AthleteId", "Scope",
                   "CreatedTimestamp", "UpdatedTimestamp"
            FROM public."StravaTokens"
            WHERE "Id" = :id
            """
        )
        async with self._engine.connect() as connection:
            result = await connection.execute(sql, {"id": token_id})
            row = result.mappings().first()
            return StravaToken(**row) if row else None
