"""Thin async `httpx` wrapper around Strava's OAuth2 endpoints.

Strava has no first-party Python SDK (unlike Garmin's `garminconnect`), so this
module calls its OAuth endpoints directly. It also owns the in-memory, TTL-bounded
store for the OAuth CSRF `state` value, mirroring `garmin_client_factory.py`'s
`_PENDING_MFA_LOGINS` pattern: single-worker-process only, an accepted constraint
for this service's deployment.
"""

import secrets
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx

from ...config import get_settings

_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
_TOKEN_URL = "https://www.strava.com/oauth/token"  # noqa: S105 — URL, not a credential
_ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
_ACTIVITIES_PAGE_SIZE = 200


class StravaClientAuthenticationError(Exception):
    """Strava rejected the supplied authorization code, refresh token, or access token."""


class StravaClientConnectionError(Exception):
    """Strava could not be reached, or returned an unexpected response."""


@dataclass(frozen=True, slots=True)
class StravaTokenExchangeResult:
    access_token: str
    refresh_token: str
    expires_at: datetime
    athlete_id: int
    scope: str


@dataclass(frozen=True, slots=True)
class StravaTokenRefreshResult:
    access_token: str
    refresh_token: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class StravaActivitySummaryDTO:
    id: int
    name: str
    type: str
    sport_type: str
    start_date: datetime
    start_date_local: datetime
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    average_heartrate: float | None
    max_heartrate: float | None
    gear_id: str | None


# Pending Strava authorizations waiting on their callback, keyed by the generated
# `state` value, mapped to its expiry (monotonic clock). Single-worker-process only,
# the same accepted constraint as Garmin's `_PENDING_MFA_LOGINS`.
_PENDING_STATES: dict[str, float] = {}
_pending_states_lock = threading.Lock()


def build_authorize_url(state: str) -> str:
    """Build Strava's authorization URL for the given (already-generated) state."""
    settings = get_settings()
    params = {
        "client_id": settings.strava_client_id,
        "redirect_uri": settings.strava_redirect_uri,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": ",".join(settings.strava_scope),
        "state": state,
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


def generate_pending_state() -> str:
    """Generate a cryptographically random, single-use `state` value and store it,
    pending the OAuth callback."""
    state = secrets.token_urlsafe(32)
    _store_pending_state(state)
    return state


def consume_pending_state(state: str) -> bool:
    """Return True and invalidate the state if it was pending and not expired."""
    return _pop_pending_state(state)


async def _post_to_token_endpoint(data: dict[str, str], *, rejection_message: str) -> dict:
    """POST to Strava's /oauth/token endpoint (shared by an authorization-code exchange and
    a refresh-token exchange) and return the parsed JSON body. Raises
    StravaClientAuthenticationError if Strava rejects the code/token, StravaClientConnectionError
    on any other failure."""
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                _TOKEN_URL,
                data={
                    "client_id": settings.strava_client_id,
                    "client_secret": settings.strava_client_secret,
                    **data,
                },
            )
        except httpx.HTTPError as exc:
            raise StravaClientConnectionError(str(exc)) from exc

    if response.status_code in (400, 401):
        raise StravaClientAuthenticationError(rejection_message)
    if response.status_code >= 400:
        raise StravaClientConnectionError(
            f"Strava token endpoint failed with status {response.status_code}."
        )
    return response.json()


async def exchange_code_for_token(code: str) -> StravaTokenExchangeResult:
    """Exchange an authorization code for tokens. Raises StravaClientAuthenticationError
    if Strava rejects the code, StravaClientConnectionError on any other failure."""
    body = await _post_to_token_endpoint(
        {"code": code, "grant_type": "authorization_code"},
        rejection_message="Strava rejected the supplied authorization code.",
    )

    athlete = body.get("athlete") or {}
    access_token = body.get("access_token")
    refresh_token = body.get("refresh_token")
    expires_at = body.get("expires_at")
    athlete_id = athlete.get("id")
    scope = body.get("scope")
    if not access_token or not refresh_token or expires_at is None or athlete_id is None:
        raise StravaClientConnectionError("Strava token exchange returned an unexpected response.")

    return StravaTokenExchangeResult(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.fromtimestamp(expires_at, tz=UTC),
        athlete_id=athlete_id,
        scope=scope or "",
    )


async def refresh_access_token(refresh_token: str) -> StravaTokenRefreshResult:
    """Exchange a stored refresh token for a new access token. Raises
    StravaClientAuthenticationError if Strava rejects the refresh token,
    StravaClientConnectionError on any other failure."""
    body = await _post_to_token_endpoint(
        {"refresh_token": refresh_token, "grant_type": "refresh_token"},
        rejection_message="Strava rejected the stored refresh token.",
    )

    access_token = body.get("access_token")
    new_refresh_token = body.get("refresh_token")
    expires_at = body.get("expires_at")
    if not access_token or not new_refresh_token or expires_at is None:
        raise StravaClientConnectionError("Strava token refresh returned an unexpected response.")

    return StravaTokenRefreshResult(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_at=datetime.fromtimestamp(expires_at, tz=UTC),
    )


async def list_activities(
    access_token: str, *, after: int, before: int
) -> list[StravaActivitySummaryDTO]:
    """Fetch every activity Strava reports between the given epoch-second `after`/`before`
    bounds, paginating at `_ACTIVITIES_PAGE_SIZE` per page until a short page signals the end.
    Raises StravaClientAuthenticationError if Strava rejects the access token,
    StravaClientConnectionError on any other failure."""
    activities: list[StravaActivitySummaryDTO] = []
    page = 1
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(
                    _ACTIVITIES_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "after": after,
                        "before": before,
                        "page": page,
                        "per_page": _ACTIVITIES_PAGE_SIZE,
                    },
                )
            except httpx.HTTPError as exc:
                raise StravaClientConnectionError(str(exc)) from exc

            if response.status_code == 401:
                raise StravaClientAuthenticationError("Strava rejected the supplied access token.")
            if response.status_code >= 400:
                raise StravaClientConnectionError(
                    f"Strava list activities failed with status {response.status_code}."
                )

            page_activities = [_parse_activity_summary(item) for item in response.json()]
            activities.extend(page_activities)
            if len(page_activities) < _ACTIVITIES_PAGE_SIZE:
                break
            page += 1

    return activities


def _parse_activity_summary(item: dict) -> StravaActivitySummaryDTO:
    return StravaActivitySummaryDTO(
        id=item["id"],
        name=item["name"],
        type=item["type"],
        sport_type=item["sport_type"],
        start_date=datetime.fromisoformat(item["start_date"]),
        start_date_local=datetime.fromisoformat(item["start_date_local"]),
        distance=item["distance"],
        moving_time=item["moving_time"],
        elapsed_time=item["elapsed_time"],
        total_elevation_gain=item["total_elevation_gain"],
        average_heartrate=item.get("average_heartrate"),
        max_heartrate=item.get("max_heartrate"),
        gear_id=item.get("gear_id"),
    )


async def get_authenticated_athlete(access_token: str) -> int:
    """Call Strava's /athlete endpoint to verify the access token actually works.
    Returns the authenticated athlete's id."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                _ATHLETE_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
        except httpx.HTTPError as exc:
            raise StravaClientConnectionError(str(exc)) from exc

    if response.status_code == 401:
        raise StravaClientAuthenticationError("Strava rejected the exchanged access token.")
    if response.status_code >= 400:
        raise StravaClientConnectionError(
            f"Strava athlete verification failed with status {response.status_code}."
        )

    athlete_id = response.json().get("id")
    if athlete_id is None:
        raise StravaClientConnectionError("Strava athlete verification returned no athlete id.")
    return athlete_id


def _store_pending_state(state: str) -> None:
    ttl_seconds = get_settings().strava_state_ttl_seconds
    with _pending_states_lock:
        _prune_expired_states()
        _PENDING_STATES[state] = time.monotonic() + ttl_seconds


def _pop_pending_state(state: str) -> bool:
    with _pending_states_lock:
        _prune_expired_states()
        expires_at = _PENDING_STATES.pop(state, None)
    return expires_at is not None


def _prune_expired_states() -> None:
    now = time.monotonic()
    expired = [s for s, expires_at in _PENDING_STATES.items() if expires_at <= now]
    for s in expired:
        del _PENDING_STATES[s]
