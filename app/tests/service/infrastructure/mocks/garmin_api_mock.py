"""Mocks the Garmin Connect client boundary for service tests.

`garminconnect` itself is trusted and is never mocked directly (per the
developer's ISSUE-2 review); instead these helpers patch the functions this
service calls it through, at `infrastructure/garmin/garmin_client_factory.py`.
"""

from typing import Any

from pytest_mock import MockerFixture

from health_dashboard_service.infrastructure.garmin import garmin_client_factory
from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminClientAuthenticationError,
    GarminClientConnectionError,
    GarminDailySnapshot,
)


def configure_successful_login(mocker: MockerFixture, token_data: str) -> Any:
    return mocker.patch.object(
        garmin_client_factory, "login_and_dump_token", return_value=token_data
    )


def configure_login_rejected(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "login_and_dump_token",
        side_effect=GarminClientAuthenticationError("Garmin rejected the supplied credentials."),
    )


def configure_login_unreachable(mocker: MockerFixture) -> Any:
    return mocker.patch.object(
        garmin_client_factory,
        "login_and_dump_token",
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
