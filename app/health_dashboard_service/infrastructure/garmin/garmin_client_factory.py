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

from dataclasses import dataclass
from datetime import date

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)


class GarminClientAuthenticationError(Exception):
    """Garmin Connect rejected the supplied credentials or stored session."""


class GarminClientConnectionError(Exception):
    """Garmin Connect could not be reached, or returned an unexpected error."""


@dataclass(frozen=True, slots=True)
class GarminDailySnapshot:
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    body_battery: int | None


def login_and_dump_token(email: str, password: str) -> str:
    """Log in with credentials and return the resulting session token data."""
    client = Garmin(email=email, password=password)
    _login(client)
    return client.client.dumps()


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


def _login(client: Garmin, tokenstore: str | None = None) -> None:
    try:
        client.login(tokenstore=tokenstore)
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
