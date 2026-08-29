import logging
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ...config import Settings, get_settings

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None


def build_dsn(settings: Settings) -> str:
    password = quote_plus(settings.pg_password)
    user = quote_plus(settings.pg_user)
    return (
        f"postgresql+asyncpg://{user}:{password}"
        f"@{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"
    )


async def init_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create the process-wide engine and verify the database is reachable."""
    global _engine

    settings = settings or get_settings()
    _engine = create_async_engine(
        build_dsn(settings),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,
        echo=settings.db_echo,
    )

    await verify_connectivity(_engine)
    logger.info(
        "Database engine initialised (host=%s database=%s pool_size=%s)",
        settings.pg_host,
        settings.pg_database,
        settings.db_pool_size,
    )
    return _engine


async def verify_connectivity(engine: AsyncEngine | None = None) -> None:
    """Issue a trivial query to confirm the database answers."""
    engine = engine or get_engine()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Engine not initialised — call init_engine() at startup.")
    return _engine
