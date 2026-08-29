from uuid import UUID

from ....infrastructure.postgres.persistence_controller import PersistenceController
from .template_entities import Template


async def get_by_id(pc: PersistenceController, template_id: UUID) -> Template | None:
    row = await pc.query_single_or_default(
        """
        SELECT "Id", "Name", "CreatedTimestamp", "UpdatedTimestamp", "Deleted"
        FROM public."Templates"
        WHERE "Id" = :template_id AND "Deleted" = FALSE
        """,
        {"template_id": template_id},
    )
    return Template(**row) if row else None


async def get_page(pc: PersistenceController, limit: int, offset: int) -> list[Template]:
    rows = await pc.query(
        """
        SELECT "Id", "Name", "CreatedTimestamp", "UpdatedTimestamp", "Deleted"
        FROM public."Templates"
        WHERE "Deleted" = FALSE
        ORDER BY "CreatedTimestamp" DESC, "Id"
        LIMIT :limit OFFSET :offset
        """,
        {"limit": limit, "offset": offset},
    )
    return [Template(**row) for row in rows]


async def count(pc: PersistenceController) -> int:
    row = await pc.query_single(
        """
        SELECT COUNT(*) AS "Total"
        FROM public."Templates"
        WHERE "Deleted" = FALSE
        """
    )
    return int(row["Total"])


async def exists(pc: PersistenceController, template_id: UUID) -> bool:
    row = await pc.query_single_or_default(
        """
        SELECT 1 AS "Found"
        FROM public."Templates"
        WHERE "Id" = :template_id AND "Deleted" = FALSE
        """,
        {"template_id": template_id},
    )
    return row is not None
