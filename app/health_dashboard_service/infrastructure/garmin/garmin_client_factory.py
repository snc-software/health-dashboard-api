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
    peak_body_battery: int | None
    sleep_score: int | None
    hrv_last_night_average: int | None
    hrv_status: str | None
    training_readiness_score: int | None
    training_status: str | None
    spo2_average: int | None
    vo2_max: float | None
    fitness_age: float | None
    weight_grams: int | None
    intensity_minutes: int | None


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
        hrv = client.get_hrv_data(cdate)
        readiness = client.get_training_readiness(cdate)
        status = client.get_training_status(cdate)
        spo2 = client.get_spo2_data(cdate)
        # SDK type hint claims dict[str, Any]; observed live response is actually a list
        # (one entry per day in the range, see _extract_max_metrics).
        max_metrics = cast(list[dict], client.get_max_metrics(cdate))
        weigh_ins = client.get_daily_weigh_ins(cdate)
        intensity = client.get_intensity_minutes_data(cdate)
    except (GarminConnectConnectionError, GarminConnectTooManyRequestsError) as exc:
        raise GarminClientConnectionError(str(exc)) from exc

    vo2_max, fitness_age = _extract_max_metrics(max_metrics)
    hrv_last_night_average, hrv_status = _extract_hrv(hrv)

    return GarminDailySnapshot(
        steps=stats.get("totalSteps"),
        resting_heart_rate=stats.get("restingHeartRate"),
        sleep_seconds=_extract_sleep_seconds(sleep),
        peak_body_battery=_extract_peak_body_battery(battery),
        sleep_score=_extract_sleep_score(sleep),
        hrv_last_night_average=hrv_last_night_average,
        hrv_status=hrv_status,
        training_readiness_score=_extract_training_readiness_peak(readiness),
        training_status=_extract_training_status(status),
        spo2_average=_extract_spo2_average(spo2),
        vo2_max=vo2_max,
        fitness_age=fitness_age,
        weight_grams=_extract_latest_weight(weigh_ins),
        intensity_minutes=_extract_intensity_minutes(intensity),
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


def _extract_sleep_score(sleep: dict | None) -> int | None:
    daily_sleep = sleep.get("dailySleepDTO") if sleep else None
    scores = daily_sleep.get("sleepScores") if daily_sleep else None
    overall = scores.get("overall") if scores else None
    # Assumed shape (NEEDS CONFIRMING against a live response, see plans/ISSUE-5-*): the overall
    # sleep score sits at dailySleepDTO.sleepScores.overall.value, alongside per-stage sub-scores.
    return overall.get("value") if overall else None


def _extract_peak_body_battery(battery: list[dict] | None) -> int | None:
    if not battery:
        return None
    values = battery[0].get("bodyBatteryValuesArray") or []
    if not values:
        return None
    # Each entry is [timestamp, value, status, version]; value is null for gaps in the
    # timeline (e.g. when the device wasn't worn), so those must be filtered before
    # taking the peak value across the day.
    levels = [entry[1] for entry in values if entry[1] is not None]
    return max(levels) if levels else None


def _extract_hrv(hrv: dict | None) -> tuple[int | None, str | None]:
    # Assumed shape (NEEDS CONFIRMING, see plans/ISSUE-5-*): hrvSummary.lastNightAvg (ms) and
    # hrvSummary.status (e.g. "BALANCED"). get_hrv_data itself may return None outright.
    summary = hrv.get("hrvSummary") if hrv else None
    if not summary:
        return None, None
    return summary.get("lastNightAvg"), summary.get("status")


def _extract_training_readiness_peak(readiness: list[dict] | None) -> int | None:
    if not readiness:
        return None
    scores = [score for entry in readiness if (score := entry.get("score")) is not None]
    return max(scores) if scores else None


# Confirmed against a live response: trainingStatus is an integer enum code (Garmin's own
# app renders these via a fixed lookup), not a string label directly.
_TRAINING_STATUS_LABELS: dict[int, str] = {
    0: "NO_STATUS",
    1: "DETRAINING",
    2: "RECOVERY",
    3: "MAINTAINING",
    4: "PRODUCTIVE",
    5: "PEAKING",
    6: "OVERREACHING",
    7: "STRAINED",
    8: "UNPRODUCTIVE",
}


def _extract_training_status(status: dict | None) -> str | None:
    # Confirmed shape: mostRecentTrainingStatus.latestTrainingStatusData is a dict keyed by
    # device id, each entry carrying a numeric trainingStatus code (see _TRAINING_STATUS_LABELS).
    most_recent = status.get("mostRecentTrainingStatus") if status else None
    latest_by_device = most_recent.get("latestTrainingStatusData") if most_recent else None
    if not latest_by_device:
        return None
    device_entry = next(iter(latest_by_device.values()), None)
    code = device_entry.get("trainingStatus") if device_entry else None
    if code is None:
        return None
    return _TRAINING_STATUS_LABELS.get(code, str(code))


def _extract_spo2_average(spo2: dict | None) -> int | None:
    # Assumed field name (NEEDS CONFIRMING, see plans/ISSUE-5-*).
    return spo2.get("averageSpO2") if spo2 else None


def _extract_max_metrics(metrics: list[dict] | None) -> tuple[float | None, float | None]:
    # Confirmed against a live response: get_max_metrics returns a list (one entry per day
    # in the requested range), not the dict its own type hint claims. VO2max and fitness age
    # sit under a "generic" (non-cycling) sub-object on that day's entry.
    if not metrics:
        return None, None
    generic = metrics[0].get("generic")
    if not generic:
        return None, None
    return generic.get("vo2MaxValue"), generic.get("fitnessAge")


def _extract_latest_weight(weigh_ins: dict | None) -> int | None:
    entries = weigh_ins.get("dateWeightList") if weigh_ins else None
    if not entries:
        return None
    # Expected to contain a single entry per day; take the latest by timestamp defensively in
    # case more than one is ever returned. Weight is already in grams.
    latest = max(entries, key=lambda entry: entry.get("timestampGMT") or entry.get("date") or 0)
    return latest.get("weight")


def _extract_intensity_minutes(intensity: dict | None) -> int | None:
    # Assumed field name (NEEDS CONFIRMING, see plans/ISSUE-5-*): a single rolled-up total for
    # the day (Garmin's own moderate + 2x vigorous weighting already applied).
    return intensity.get("totalIntensityMinutes") if intensity else None
