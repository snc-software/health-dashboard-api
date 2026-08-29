import asyncio
import logging
from datetime import UTC, date, datetime

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from ..contracts.common import ProblemDetails
from ..contracts.garmin import AuthenticateGarminRequest, GarminDailyStatResponse
from ..features.garmin import garmin_mapper as mapper
from ..features.garmin.domain import garmin_service as service
from ..features.garmin.domain.garmin_service import (
    GarminAuthenticationError,
    GarminServiceError,
    GarminSessionNotFoundError,
)
from ..infrastructure.logging import values as log_values
from ..openapi import open_api_tags as OAPI
from ..openapi import responses as OAPIResponses
from ..openapi.responses import Responses

logger = logging.getLogger("garmin")

router = APIRouter()

_GARMIN_UNAUTHORIZED: Responses = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ProblemDetails,
        "description": "Garmin Connect rejected the supplied credentials",
    }
}
_GARMIN_NO_SESSION: Responses = {
    status.HTTP_409_CONFLICT: {
        "model": ProblemDetails,
        "description": "No Garmin session has been established yet",
    }
}
_GARMIN_UNREACHABLE: Responses = {
    status.HTTP_502_BAD_GATEWAY: {
        "model": ProblemDetails,
        "description": "Garmin Connect is unreachable, or rejected the stored session",
    }
}


@router.post(
    "/garmin/authenticate",
    summary="Authenticate against Garmin Connect",
    description=(
        "Exchanges Garmin Connect credentials for a session token, stored in Postgres. "
        "The email/password are used once for this request and are never persisted."
    ),
    tags=OAPI.GARMIN,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_GARMIN_UNAUTHORIZED,
        **_GARMIN_UNREACHABLE,
        **OAPIResponses.SERVER_ERROR,
    },
)
def authenticate_garmin(body: AuthenticateGarminRequest) -> None:
    logger.info("authenticate_garmin called")

    credentials = mapper.map_from_contract_to_domain_credentials(body)
    try:
        asyncio.run(service.authenticate(credentials))
    except GarminAuthenticationError as exc:
        logger.info("authenticate_garmin rejected by Garmin")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except GarminServiceError as exc:
        logger.warning("authenticate_garmin failed: Garmin unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info("authenticate_garmin succeeded")


@router.post(
    "/garmin/refresh",
    summary="Refresh daily Garmin stats",
    description=(
        "Uses the stored Garmin session to pull the day's summary stats and upserts them "
        "into Postgres, without requiring credentials again."
    ),
    tags=OAPI.GARMIN,
    response_model=GarminDailyStatResponse,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_GARMIN_NO_SESSION,
        **_GARMIN_UNREACHABLE,
        **OAPIResponses.SERVER_ERROR,
    },
)
def refresh_garmin_data(stat_date: date | None = None) -> GarminDailyStatResponse:
    resolved_date = stat_date or datetime.now(UTC).date()
    logger.info("refresh_garmin_data called", extra={log_values.STAT_DATE: resolved_date})

    try:
        stat = asyncio.run(service.refresh_daily_stats(resolved_date))
    except GarminSessionNotFoundError as exc:
        logger.info("refresh_garmin_data has no stored session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except GarminServiceError as exc:
        logger.warning("refresh_garmin_data failed: Garmin unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info("refresh_garmin_data succeeded", extra={log_values.STAT_DATE: resolved_date})
    return mapper.map_from_domain_to_response_daily_stat(stat)
