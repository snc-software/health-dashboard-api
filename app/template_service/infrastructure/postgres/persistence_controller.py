from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncTransaction


class PersistenceController:
    """
    Persistence context implementing the Unit of Work pattern.

    `save_changes()` commits; `dispose()` releases the connection, rolling back
    first if nothing was committed. Obtain one via `create_persistence_controller()`
    rather than constructing it directly, so disposal is guaranteed.
    """

    def __init__(self, connection: AsyncConnection):
        self.connection = connection
        self.transaction: AsyncTransaction | None = None
        self._committed = False
        self._disposed = False

    async def start_transaction_manually(self) -> None:
        """Ensure a transaction is open."""
        if self.transaction is None:
            self.transaction = await self.connection.begin()

    async def save_changes(self) -> None:
        """Commit the open transaction, if any. Does not close the connection."""
        if self.transaction is not None:
            await self.transaction.commit()
            self.transaction = None
        self._committed = True

    async def rollback(self) -> None:
        """Roll back the open transaction, if any."""
        if self.transaction is not None:
            await self.transaction.rollback()
            self.transaction = None

    async def dispose(self) -> None:
        """Roll back an uncommitted unit of work and release the connection."""
        if self._disposed:
            return
        self._disposed = True
        try:
            if not self._committed:
                await self.rollback()
        finally:
            await self.connection.close()

    async def query_single_or_default(
        self, sql: str, parameters: dict | None = None
    ) -> dict | None:
        result = await self.connection.execute(text(sql), parameters or {})
        row = result.mappings().first()
        return dict(row) if row else None

    async def query_single(self, sql: str, parameters: dict | None = None) -> dict:
        result = await self.connection.execute(text(sql), parameters or {})
        return dict(result.mappings().one())

    async def query(self, sql: str, parameters: dict | None = None) -> Sequence[dict]:
        result = await self.connection.execute(text(sql), parameters or {})
        return [dict(row) for row in result.mappings().all()]

    async def execute(self, sql: str, parameters: dict | None = None) -> int:
        await self.start_transaction_manually()
        result = await self.connection.execute(text(sql), parameters or {})
        return result.rowcount

    async def execute_with_results(
        self, sql: str, parameters: dict | None = None
    ) -> Sequence[dict]:
        await self.start_transaction_manually()
        result = await self.connection.execute(text(sql), parameters or {})
        return [dict(row) for row in result.mappings().all()]

    async def execute_with_result(self, sql: str, parameters: dict | None = None) -> dict:
        await self.start_transaction_manually()
        result = await self.connection.execute(text(sql), parameters or {})
        return dict(result.mappings().one())

    async def execute_with_result_or_default(
        self, sql: str, parameters: dict | None = None
    ) -> dict | None:
        await self.start_transaction_manually()
        result = await self.connection.execute(text(sql), parameters or {})
        row = result.mappings().first()
        return dict(row) if row else None

    async def __aenter__(self) -> PersistenceController:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.dispose()
