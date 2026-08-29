from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from .connection_factory import get_engine
from .persistence_controller import PersistenceController


@asynccontextmanager
async def create_persistence_controller() -> AsyncGenerator[PersistenceController]:
    """
    Open a unit of work for the duration of the `async with` block.

    On exit the transaction is rolled back unless `save_changes()` was called,
    and the connection is returned to the pool either way.
    """
    connection = await get_engine().connect()
    async with PersistenceController(connection) as controller:
        yield controller
