"""Thin, synchronous wrapper around the `garminconnect` package.

`garminconnect` is a synchronous SDK. Wrapping it in `asyncio.to_thread` would
only fake cancellation support without removing the underlying blocking network
calls, so this module — and the two `routes/garmin.py` handlers that call into
it — stay synchronous (an accepted, scoped deviation from `endpoint-standards.md`,
confirmed by the developer during the ISSUE-2 plan review).

`garminconnect` itself is trusted and never mocked; service tests mock the
functions in this module instead (see `service-test-standards.md`'s confirmed
mocking deviation).
"""

import threading
import time
import uuid
from dataclasses import dataclass
from datetime import date
from typing import cast

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from ...config import get_settings


class GarminClientAuthenticationError(Exception):
    """Garmin Connect rejected the supplied credentials or stored session."""


class GarminClientConnectionError(Exception):
    """Garmin Connect could not be reached, or returned an unexpected error."""


class GarminClientMfaSessionNotFoundError(Exception):
    """No pending Garmin MFA login was found for the supplied session id (unknown or expired)."""


@dataclass(frozen=True, slots=True)
class GarminDailySnapshot:
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    body_battery: int | None


@dataclass(frozen=True, slots=True)
class GarminLoginResult:
    mfa_required: bool
    mfa_session_id: uuid.UUID | None
    token_data: str | None


# Pending Garmin logins that stopped at an MFA challenge, keyed by a generated session
# id. The live `Garmin` client must be kept in memory because `resume_login`'s pending
# state lives on the client instance itself and cannot be serialised (see module docstring
# constraint noted during the ISSUE-2 MFA plan review). Single-worker-process only.
_PENDING_MFA_LOGINS: dict[uuid.UUID, tuple[Garmin, float]] = {}
_pending_mfa_lock = threading.Lock()


def start_login(email: str, password: str) -> GarminLoginResult:
    """Start a Garmin login. Returns immediately with an MFA session id instead of
    blocking on a prompt if Garmin challenges for an MFA code."""
    client = Garmin(email=email, password=password, return_on_mfa=True)
    mfa_status, _ = _login(client)

    if mfa_status is None:
        token_data = cast(str, client.client.dumps())
        return GarminLoginResult(mfa_required=False, mfa_session_id=None, token_data=token_data)

    session_id = uuid.uuid4()
    _store_pending_login(session_id, client)
    return GarminLoginResult(mfa_required=True, mfa_session_id=session_id, token_data=None)


def complete_mfa_login(mfa_session_id: uuid.UUID, mfa_code: str) -> str:
    """Submit an MFA code for a previously started login and return the resulting
    session token data."""
    client = _pop_pending_login(mfa_session_id)
    if client is None:
        raise GarminClientMfaSessionNotFoundError(
            f"No pending Garmin MFA login found for session {mfa_session_id}"
        )

    try:
        client.resume_login({}, mfa_code)
    except GarminConnectAuthenticationError as exc:
        raise GarminClientAuthenticationError(str(exc)) from exc
    except (GarminConnectConnectionError, GarminConnectTooManyRequestsError) as exc:
        raise GarminClientConnectionError(str(exc)) from exc

    return cast(str, client.client.dumps())


def _store_pending_login(session_id: uuid.UUID, client: Garmin) -> None:
    ttl_seconds = get_settings().garmin_mfa_session_ttl_seconds
    with _pending_mfa_lock:
        _prune_expired_logins()
        _PENDING_MFA_LOGINS[session_id] = (client, time.monotonic() + ttl_seconds)


def _pop_pending_login(session_id: uuid.UUID) -> Garmin | None:
    with _pending_mfa_lock:
        _prune_expired_logins()
        entry = _PENDING_MFA_LOGINS.pop(session_id, None)
    return entry[0] if entry else None


def _prune_expired_logins() -> None:
    now = time.monotonic()
    expired = [sid for sid, (_, expires_at) in _PENDING_MFA_LOGINS.items() if expires_at <= now]
    for sid in expired:
        del _PENDING_MFA_LOGINS[sid]


def fetch_daily_snapshot(token_data: str, stat_date: date) -> GarminDailySnapshot:
    """Resume a session from a stored token and pull one day's summary stats."""
    client = Garmin()
    _login(client, tokenstore=token_data)

    cdate = stat_date.isoformat()
    try:
        stats = client.get_stats(cdate)
        sleep = client.get_sleep_data(cdate)
        battery = client.get_body_battery(cdate)
    except (GarminConnectConnectionError, GarminConnectTooManyRequestsError) as exc:
        raise GarminClientConnectionError(str(exc)) from exc

    return GarminDailySnapshot(
        steps=stats.get("totalSteps"),
        resting_heart_rate=stats.get("restingHeartRate"),
        sleep_seconds=_extract_sleep_seconds(sleep),
        body_battery=_extract_body_battery(battery),
    )


def _login(client: Garmin, tokenstore: str | None = None) -> tuple[str | None, str | None]:
    try:
        return cast(tuple[str | None, str | None], client.login(tokenstore=tokenstore))
    except GarminConnectAuthenticationError as exc:
        raise GarminClientAuthenticationError(str(exc)) from exc
    except (GarminConnectConnectionError, GarminConnectTooManyRequestsError) as exc:
        raise GarminClientConnectionError(str(exc)) from exc


def _extract_sleep_seconds(sleep: dict | None) -> int | None:
    daily_sleep = sleep.get("dailySleepDTO") if sleep else None
    return daily_sleep.get("sleepTimeSeconds") if daily_sleep else None


def _extract_body_battery(battery: list[dict] | None) -> int | None:
    if not battery:
        return None
    values = battery[0].get("bodyBatteryValuesArray") or []
    if not values:
        return None
    # Each entry is [timestamp, value, status, version]; take the most recent value.
    return values[-1][1]
