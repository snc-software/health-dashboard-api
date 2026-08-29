import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import DocumentDownloadType, Theme, get_scalar_api_reference

from . import routes
from .config import get_settings
from .infrastructure.http.exception_handlers import register_exception_handlers
from .infrastructure.logging import configure_logging
from .infrastructure.postgres.connection_factory import close_engine, init_engine
from .openapi import open_api_tags as OAPI
from .openapi.schema import configure_openapi

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    logger.info(
        "Starting %s v%s (%s)", settings.app_name, settings.app_version, settings.environment
    )

    await init_engine(settings)
    try:
        yield
    finally:
        await close_engine()
        logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Build and wire the application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_name,
        version=settings.app_version,
        openapi_tags=OAPI.ALL_TAGS,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
        )

    register_exception_handlers(app)
    configure_openapi(app)

    for router in routes.routers:
        app.include_router(router)

    @app.get("/docs", include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            dark_mode=True,
            theme=Theme.MOON,
            show_developer_tools="never",
            show_sidebar=True,
            document_download_type=DocumentDownloadType.JSON,
            telemetry=False,
        )

    return app


app = create_app()
