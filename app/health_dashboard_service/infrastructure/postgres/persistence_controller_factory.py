from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from ...config import get_settings
from .connection_factory import build_dsn, get_engine
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


@asynccontextmanager
async def create_scoped_persistence_controller() -> AsyncGenerator[PersistenceController]:
    """
    Open a unit of work backed by a fresh, unpooled connection.

    For callers that bridge into this async layer from a synchronous entry point via
    `asyncio.run()` (a new event loop per call, e.g. `routes/garmin.py`'s two sync
    handlers) — reusing the shared, pooled engine's connections across those short-lived
    loops raises `RuntimeError: ... attached to a different loop`, since asyncpg
    connections are bound to the loop that opened them. `NullPool` sidesteps this by
    never caching a connection between calls.
    """
    engine = create_async_engine(build_dsn(get_settings()), poolclass=NullPool)
    try:
        connection = await engine.connect()
        async with PersistenceController(connection) as controller:
            yield controller
    finally:
        await engine.dispose()
