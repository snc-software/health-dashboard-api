import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..contracts.health import HealthResponse, ReadinessResponse
from ..infrastructure.postgres.connection_factory import verify_connectivity
from ..openapi import open_api_tags as OAPI
from ..openapi import responses as OAPIResponses

logger = logging.getLogger(__name__)

router = APIRouter(tags=OAPI.HEALTH)


@router.get(
    "/health",
    summary="Liveness probe",
    response_model=HealthResponse,
    responses={**OAPIResponses.SERVER_ERROR},
)
async def health() -> HealthResponse:
    """Report that the process is up. Touches no dependencies."""
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get(
    "/health/ready",
    summary="Readiness probe",
    response_model=ReadinessResponse,
    responses={**OAPIResponses.SERVICE_UNAVAILABLE, **OAPIResponses.SERVER_ERROR},
)
async def ready() -> JSONResponse:
    """Report whether this instance can serve traffic. Returns 503 if not."""
    try:
        await verify_connectivity()
    except Exception:
        logger.exception("Readiness check failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ReadinessResponse(status="unavailable", database="unreachable").model_dump(
                by_alias=True
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ReadinessResponse(status="ok", database="reachable").model_dump(by_alias=True),
    )
