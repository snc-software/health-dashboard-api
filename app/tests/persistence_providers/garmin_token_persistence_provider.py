"""Test-only helper for seeding and reading GarminToken rows directly against Postgres."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from health_dashboard_service.features.garmin.persistence.garmin_entities import GarminToken


class GarminTokenPersistenceProvider:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def insert(self, token: GarminToken) -> None:
        sql = text(
            """
            INSERT INTO public."GarminTokens"
                ("Id", "TokenData", "CreatedTimestamp", "UpdatedTimestamp")
            VALUES (:id, :token_data, :created_timestamp, :updated_timestamp)
            ON CONFLICT ("Id") DO UPDATE SET
                "TokenData" = EXCLUDED."TokenData",
                "UpdatedTimestamp" = EXCLUDED."UpdatedTimestamp"
            """
        )
        async with self._engine.begin() as connection:
            await connection.execute(
                sql,
                {
                    "id": token.Id,
                    "token_data": token.TokenData,
                    "created_timestamp": token.CreatedTimestamp,
                    "updated_timestamp": token.UpdatedTimestamp,
                },
            )

    async def get_by_id(self, token_id: UUID) -> GarminToken | None:
        sql = text(
            """
            SELECT "Id", "TokenData", "CreatedTimestamp", "UpdatedTimestamp"
            FROM public."GarminTokens"
            WHERE "Id" = :id
            """
        )
        async with self._engine.connect() as connection:
            result = await connection.execute(sql, {"id": token_id})
            row = result.mappings().first()
            return GarminToken(**row) if row else None
