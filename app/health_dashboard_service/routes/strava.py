import logging
from urllib.parse import urlencode

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from ..config import get_settings
from ..contracts.strava import StravaSessionResponse
from ..features.strava import strava_mapper as mapper
from ..features.strava.domain import strava_service as service
from ..features.strava.domain.strava_service import (
    StravaAuthenticationError,
    StravaServiceError,
    StravaStateInvalidError,
)
from ..infrastructure.logging import values as log_values
from ..openapi import open_api_tags as OAPI

logger = logging.getLogger("strava")

router = APIRouter()


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


def _redirect_to_ui(*, connected: bool, reason: str | None = None) -> RedirectResponse:
    params: dict[str, str] = {"stravaConnected": "true" if connected else "false"}
    if reason is not None:
        params["reason"] = reason
    ui_url = f"{get_settings().strava_ui_redirect_url}?{urlencode(params)}"
    return RedirectResponse(url=ui_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
