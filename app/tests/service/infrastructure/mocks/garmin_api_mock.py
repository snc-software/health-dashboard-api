"""Mocks the Garmin Connect client boundary for service tests.

`garminconnect` itself is trusted and is never mocked directly (per the
developer's ISSUE-2 review); instead these helpers patch the functions this
service calls it through, at `infrastructure/garmin/garmin_client_factory.py`.
"""

import uuid
from datetime import date
from typing import Any

from pytest_mock import MockerFixture

from health_dashboard_service.infrastructure.garmin import garmin_client_factory
from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminClientAuthenticationError,
    GarminClientConnectionError,
    GarminClientMfaSessionNotFoundError,
    GarminDailySnapshot,
    GarminLoginResult,
)


def configure_successful_login(mocker: MockerFixture, token_data: str) -> Any:
    result = GarminLoginResult(mfa_required=False, mfa_session_id=None, token_data=token_data)
    return mocker.patch.object(garmin_client_factory, "start_login", return_value=result)


def configure_mfa_required_login(mocker: MockerFixture, mfa_session_id: uuid.UUID) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "start_login",
        return_value=GarminLoginResult(
            mfa_required=True, mfa_session_id=mfa_session_id, token_data=None
        ),
    )


def configure_login_rejected(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "start_login",
        side_effect=GarminClientAuthenticationError("Garmin rejected the supplied credentials."),
    )


def configure_login_unreachable(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "start_login",
        side_effect=GarminClientConnectionError("Garmin Connect is unreachable."),
    )


def configure_successful_mfa_completion(mocker: MockerFixture, token_data: str) -> Any:
    return mocker.patch.object(garmin_client_factory, "complete_mfa_login", return_value=token_data)


def configure_mfa_rejected(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "complete_mfa_login",
        side_effect=GarminClientAuthenticationError("Garmin rejected the supplied MFA code."),
    )


def configure_mfa_session_unknown(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "complete_mfa_login",
        side_effect=GarminClientMfaSessionNotFoundError("No pending Garmin MFA login found."),
    )


def configure_mfa_completion_unreachable(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "complete_mfa_login",
        side_effect=GarminClientConnectionError("Garmin Connect is unreachable."),
    )


def configure_daily_snapshot(mocker: MockerFixture, snapshot: GarminDailySnapshot) -> Any:
    return mocker.patch.object(garmin_client_factory, "fetch_daily_snapshot", return_value=snapshot)


def configure_daily_snapshot_unreachable(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "fetch_daily_snapshot",
        side_effect=GarminClientConnectionError("Garmin Connect is unreachable."),
    )


def configure_daily_snapshots(
    mocker: MockerFixture, snapshots_by_date: dict[date, GarminDailySnapshot]
) -> Any:
    def fetch(token_data: str, stat_date: date) -> GarminDailySnapshot:
        return snapshots_by_date[stat_date]

    return mocker.patch.object(garmin_client_factory, "fetch_daily_snapshot", side_effect=fetch)


def configure_daily_snapshots_with_failure(
    mocker: MockerFixture,
    snapshots_by_date: dict[date, GarminDailySnapshot],
    failing_dates: set[date],
) -> Any:
    def fetch(token_data: str, stat_date: date) -> GarminDailySnapshot:
        if stat_date in failing_dates:
            raise GarminClientConnectionError("Garmin Connect is unreachable.")
        return snapshots_by_date[stat_date]

    return mocker.patch.object(garmin_client_factory, "fetch_daily_snapshot", side_effect=fetch)
