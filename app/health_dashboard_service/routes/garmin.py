import asyncio
import logging

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from ..contracts.common import ProblemDetails
from ..contracts.garmin import (
    AuthenticateGarminRequest,
    BatchUpsertGarminDailyStatsRequest,
    BatchUpsertGarminDailyStatsResponse,
    GarminAuthenticateResponse,
    GarminDailyStatResponse,
    GarminSessionResponse,
    SubmitGarminMfaRequest,
    UpsertGarminDailyStatRequest,
)
from ..features.garmin import garmin_mapper as mapper
from ..features.garmin.domain import garmin_service as service
from ..features.garmin.domain.garmin_service import (
    GarminAuthenticationError,
    GarminMfaSessionNotFoundError,
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
_GARMIN_MFA_SESSION_UNKNOWN: Responses = {
    status.HTTP_409_CONFLICT: {
        "model": ProblemDetails,
        "description": "The Garmin MFA session is unknown or has expired",
    }
}


@router.post(
    "/authenticate-garmin",
    summary="Authenticate against Garmin Connect",
    description=(
        "Starts a Garmin Connect login. Returns status=authenticated and stores the resulting "
        "session token in Postgres, or status=mfa_required with a session id to submit to "
        "/authenticate-garmin-mfa if Garmin challenges for an MFA code. "
        "The email/password are used once for this request and are never persisted."
    ),
    tags=OAPI.GARMIN,
    response_model=GarminAuthenticateResponse,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_GARMIN_UNAUTHORIZED,
        **_GARMIN_UNREACHABLE,
        **OAPIResponses.SERVER_ERROR,
    },
)
def authenticate_garmin(body: AuthenticateGarminRequest) -> GarminAuthenticateResponse:
    logger.info("authenticate_garmin called")

    credentials = mapper.map_from_contract_to_domain_credentials(body)
    try:
        result = asyncio.run(service.authenticate(credentials))
    except GarminAuthenticationError as exc:
        logger.info("authenticate_garmin rejected by Garmin")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except GarminServiceError as exc:
        logger.warning("authenticate_garmin failed: Garmin unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info(
        "authenticate_garmin succeeded", extra={log_values.GARMIN_AUTH_STATUS: result.status}
    )
    return mapper.map_from_domain_to_response_authentication_result(result)


@router.post(
    "/authenticate-garmin-mfa",
    summary="Submit a Garmin Connect MFA code",
    description=(
        "Completes a Garmin Connect login previously started by /authenticate-garmin that "
        "returned status=mfa_required, persisting the resulting session token in Postgres."
    ),
    tags=OAPI.GARMIN,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_GARMIN_UNAUTHORIZED,
        **_GARMIN_MFA_SESSION_UNKNOWN,
        **_GARMIN_UNREACHABLE,
        **OAPIResponses.SERVER_ERROR,
    },
)
def submit_garmin_mfa(body: SubmitGarminMfaRequest) -> None:
    logger.info("submit_garmin_mfa called")

    submission = mapper.map_from_contract_to_domain_mfa_submission(body)
    try:
        asyncio.run(service.complete_mfa(submission))
    except GarminMfaSessionNotFoundError as exc:
        logger.info("submit_garmin_mfa has no pending session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except GarminAuthenticationError as exc:
        logger.info("submit_garmin_mfa rejected by Garmin")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except GarminServiceError as exc:
        logger.warning("submit_garmin_mfa failed: Garmin unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info("submit_garmin_mfa succeeded")


@router.get(
    "/garmin-session",
    summary="Report Garmin Connect session status",
    description=(
        "Reports whether a Garmin Connect session is currently stored, and if so, when it was "
        "last established. Never includes credentials or the raw stored session token."
    ),
    tags=OAPI.GARMIN,
    response_model=GarminSessionResponse,
    responses={**OAPIResponses.SERVER_ERROR},
)
def get_garmin_session() -> GarminSessionResponse:
    logger.info("get_garmin_session called")

    status_model = asyncio.run(service.get_session_status())

    logger.info(
        "get_garmin_session succeeded",
        extra={log_values.GARMIN_SESSION_AUTHENTICATED: status_model.authenticated},
    )
    return mapper.map_from_domain_to_response_session_status(status_model)


@router.post(
    "/garmin-daily-stats",
    summary="Upsert daily Garmin stats for a date",
    description=(
        "Uses the stored Garmin session to pull the requested date's summary stats and upserts "
        "them into Postgres, without requiring credentials again."
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
def upsert_garmin_daily_stat(body: UpsertGarminDailyStatRequest) -> GarminDailyStatResponse:
    logger.info("upsert_garmin_daily_stat called", extra={log_values.STAT_DATE: body.stat_date})

    try:
        stat = asyncio.run(service.upsert_daily_stat(body.stat_date))
    except GarminSessionNotFoundError as exc:
        logger.info("upsert_garmin_daily_stat has no stored session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except GarminServiceError as exc:
        logger.warning("upsert_garmin_daily_stat failed: Garmin unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info("upsert_garmin_daily_stat succeeded", extra={log_values.STAT_DATE: body.stat_date})
    return mapper.map_from_domain_to_response_daily_stat(stat)


@router.post(
    "/batch-garmin-daily-stats",
    summary="Backfill Garmin daily stats over a date range",
    description=(
        "Uses the stored Garmin session to pull and upsert summary stats for every date in the "
        "inclusive start_date/end_date range, sequentially. A failure on one date does not abort "
        "the rest of the range."
    ),
    tags=OAPI.GARMIN,
    response_model=BatchUpsertGarminDailyStatsResponse,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_GARMIN_NO_SESSION,
        **OAPIResponses.SERVER_ERROR,
    },
)
def batch_upsert_garmin_daily_stats(
    body: BatchUpsertGarminDailyStatsRequest,
) -> BatchUpsertGarminDailyStatsResponse:
    logger.info(
        "batch_upsert_garmin_daily_stats called",
        extra={log_values.START_DATE: body.start_date, log_values.END_DATE: body.end_date},
    )

    try:
        failed_dates = asyncio.run(service.upsert_daily_stats_range(body.start_date, body.end_date))
    except GarminSessionNotFoundError as exc:
        logger.info("batch_upsert_garmin_daily_stats has no stored session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if failed_dates:
        logger.warning(
            "batch_upsert_garmin_daily_stats completed with failures",
            extra={
                log_values.START_DATE: body.start_date,
                log_values.END_DATE: body.end_date,
                "failed_dates": [str(d) for d in failed_dates],
            },
        )
    else:
        logger.info(
            "batch_upsert_garmin_daily_stats succeeded",
            extra={log_values.START_DATE: body.start_date, log_values.END_DATE: body.end_date},
        )

    return mapper.map_from_domain_to_response_batch_upsert_result(failed_dates)
