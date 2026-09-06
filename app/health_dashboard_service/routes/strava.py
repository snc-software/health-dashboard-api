import logging
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Path, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from ..config import get_settings
from ..contracts.common import ProblemDetails
from ..contracts.strava import (
    FetchStravaActivitiesRequest,
    FetchStravaActivitiesResponse,
    GetStravaActivitiesRequest,
    GetStravaActivitySummaryRequest,
    StravaActivityResponse,
    StravaActivitySummaryResponse,
    StravaSessionResponse,
)
from ..features.strava import strava_mapper as mapper
from ..features.strava.domain import strava_service as service
from ..features.strava.domain.strava_service import (
    StravaAuthenticationError,
    StravaServiceError,
    StravaSessionNotFoundError,
    StravaStateInvalidError,
)
from ..infrastructure.logging import values as log_values
from ..openapi import open_api_tags as OAPI
from ..openapi import responses as OAPIResponses
from ..openapi.responses import Responses

logger = logging.getLogger("strava")

router = APIRouter()

_STRAVA_NO_SESSION: Responses = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ProblemDetails,
        "description": "No Strava session has been established yet",
    }
}
_STRAVA_UNAUTHORIZED: Responses = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ProblemDetails,
        "description": "Strava rejected the stored refresh token",
    }
}
_STRAVA_UNREACHABLE: Responses = {
    status.HTTP_502_BAD_GATEWAY: {
        "model": ProblemDetails,
        "description": "Strava is unreachable, or rejected the request",
    }
}


@router.get(
    "/authorize-strava",
    summary="Start Strava OAuth authorization",
    description="Redirects the browser to Strava's consent screen to begin OAuth authorization.",
    tags=OAPI.STRAVA,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
)
async def authorize_strava() -> RedirectResponse:
    logger.info("authorize_strava called")

    authorize_url = service.build_authorization_redirect_url()

    logger.info("authorize_strava redirecting to Strava")
    return RedirectResponse(url=authorize_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get(
    "/strava-callback",
    summary="Complete Strava OAuth authorization",
    description=(
        "Receives Strava's OAuth redirect, exchanges the authorization code for tokens, "
        "verifies the token against Strava's /athlete endpoint, and persists the result. "
        "Always redirects back to the configured UI with a stravaConnected flag, and never "
        "returns a JSON body, since the browser is mid-navigation from Strava."
    ),
    tags=OAPI.STRAVA,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
)
async def complete_strava_authorization(
    code: str | None = None,
    scope: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    logger.info("strava_callback called")

    try:
        await service.complete_authorization(code, state, error)
    except StravaStateInvalidError as exc:
        logger.info(
            "strava_callback rejected: invalid state",
            extra={log_values.STRAVA_CALLBACK_REASON: str(exc)},
        )
        return _redirect_to_ui(connected=False, reason="invalid_state")
    except StravaAuthenticationError as exc:
        logger.info(
            "strava_callback rejected by Strava",
            extra={log_values.STRAVA_CALLBACK_REASON: str(exc)},
        )
        return _redirect_to_ui(connected=False, reason="authentication_failed")
    except StravaServiceError as exc:
        logger.warning(
            "strava_callback failed: Strava unreachable",
            extra={log_values.STRAVA_CALLBACK_REASON: str(exc)},
        )
        return _redirect_to_ui(connected=False, reason="strava_unreachable")

    logger.info("strava_callback succeeded", extra={log_values.STRAVA_CONNECTED: True})
    return _redirect_to_ui(connected=True)


@router.get(
    "/strava-session",
    summary="Report Strava OAuth session status",
    description=(
        "Reports whether a Strava token is currently stored, and if so, the athlete id and "
        "when it was last established. Never includes the stored token."
    ),
    tags=OAPI.STRAVA,
    response_model=StravaSessionResponse,
)
async def get_strava_session() -> StravaSessionResponse:
    logger.info("get_strava_session called")

    status_model = await service.get_session_status()

    logger.info(
        "get_strava_session succeeded",
        extra={log_values.STRAVA_CONNECTED: status_model.connected},
    )
    return mapper.map_from_domain_to_response_session_status(status_model)


@router.post(
    "/strava-activities",
    summary="Fetch and store Strava activities for a date range",
    description=(
        "Uses the stored Strava session (refreshing the access token if needed) to fetch "
        "activities for the inclusive start_date/end_date range in UTC and upsert them into "
        "Postgres, returning a count of the synced activities by type."
    ),
    tags=OAPI.STRAVA,
    response_model=FetchStravaActivitiesResponse,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **_STRAVA_NO_SESSION,
        **_STRAVA_UNAUTHORIZED,
        **_STRAVA_UNREACHABLE,
        **OAPIResponses.SERVER_ERROR,
    },
)
async def fetch_strava_activities(
    body: FetchStravaActivitiesRequest,
) -> FetchStravaActivitiesResponse:
    logger.info(
        "fetch_strava_activities called",
        extra={log_values.START_DATE: body.start_date, log_values.END_DATE: body.end_date},
    )

    try:
        counts_by_type = await service.fetch_activities(body.start_date, body.end_date)
    except StravaSessionNotFoundError as exc:
        logger.info("fetch_strava_activities has no stored session")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StravaAuthenticationError as exc:
        logger.info("fetch_strava_activities rejected by Strava")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except StravaServiceError as exc:
        logger.warning("fetch_strava_activities failed: Strava unreachable")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    logger.info(
        "fetch_strava_activities succeeded",
        extra={log_values.START_DATE: body.start_date, log_values.END_DATE: body.end_date},
    )
    return mapper.map_from_domain_to_response_fetch_result(counts_by_type)


@router.get(
    "/start/{startDate}/end/{endDate}/activities",
    summary="Read stored Strava activities for a date range",
    description=(
        "Returns the Strava activities stored for the inclusive start_date/end_date range, "
        "matched against each activity's local start date, ordered ascending by start date."
    ),
    tags=OAPI.STRAVA,
    response_model=list[StravaActivityResponse],
    responses={**OAPIResponses.BAD_REQUEST, **OAPIResponses.SERVER_ERROR},
)
async def get_strava_activities(
    query: Annotated[GetStravaActivitiesRequest, Path()],
) -> list[StravaActivityResponse]:
    logger.info(
        "get_strava_activities called",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )

    activities = await service.get_activities(query.start_date, query.end_date)

    logger.info(
        "get_strava_activities succeeded",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )
    return [mapper.map_from_domain_to_response_activity(activity) for activity in activities]


@router.get(
    "/start/{startDate}/end/{endDate}/activity-summary",
    summary="Read current-vs-prior-period Strava activity stats for a date range",
    description=(
        "Computes total activity count, total Run distance, and weighted average Run pace for "
        "the inclusive start_date/end_date range (matched against each activity's local start "
        "date), alongside the same stats for the immediately preceding period of equal length."
    ),
    tags=OAPI.STRAVA,
    response_model=StravaActivitySummaryResponse,
    responses={**OAPIResponses.BAD_REQUEST, **OAPIResponses.SERVER_ERROR},
)
async def get_strava_activity_summary(
    query: Annotated[GetStravaActivitySummaryRequest, Path()],
) -> StravaActivitySummaryResponse:
    logger.info(
        "get_strava_activity_summary called",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )

    summary = await service.get_activity_summary(query.start_date, query.end_date)

    logger.info(
        "get_strava_activity_summary succeeded",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )
    return mapper.map_from_domain_to_response_activity_summary(summary)


def _redirect_to_ui(*, connected: bool, reason: str | None = None) -> RedirectResponse:
    params: dict[str, str] = {"stravaConnected": "true" if connected else "false"}
    if reason is not None:
        params["reason"] = reason
    ui_url = f"{get_settings().strava_ui_redirect_url}?{urlencode(params)}"
    return RedirectResponse(url=ui_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
