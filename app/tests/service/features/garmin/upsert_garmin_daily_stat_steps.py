"""Step implementations for the upsert-Garmin-daily-stat service test."""

from datetime import UTC, date, datetime

import httpx
from pytest_mock import MockerFixture

from health_dashboard_service.contracts.garmin import UpsertGarminDailyStatRequest
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GARMIN_TOKEN_SINGLETON_ID,
    GarminToken,
)
from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminDailySnapshot,
)
from tests.persistence_providers.garmin_daily_stat_persistence_provider import (
    GarminDailyStatPersistenceProvider,
)
from tests.persistence_providers.garmin_token_persistence_provider import (
    GarminTokenPersistenceProvider,
)
from tests.service.infrastructure.clients.garmin_client import (
    upsert_garmin_daily_stat as _call,
)
from tests.service.infrastructure.mocks import garmin_api_mock


async def upsert_garmin_daily_stat(client: httpx.AsyncClient, stat_date: date) -> httpx.Response:
    return await _call(client, UpsertGarminDailyStatRequest(stat_date=stat_date))


async def a_garmin_session_has_been_established(
    persistence_provider: GarminTokenPersistenceProvider, token_data: str = "existing-token"
) -> None:
    now = datetime.now(UTC)
    await persistence_provider.insert(
        GarminToken(
            Id=GARMIN_TOKEN_SINGLETON_ID,
            TokenData=token_data,
            CreatedTimestamp=now,
            UpdatedTimestamp=now,
        )
    )


def garmin_returns_daily_stats(mocker: MockerFixture, snapshot: GarminDailySnapshot) -> None:
    garmin_api_mock.configure_daily_snapshot(mocker, snapshot)


def garmin_is_unreachable(mocker: MockerFixture) -> None:
    garmin_api_mock.configure_daily_snapshot_unreachable(mocker)


async def assert_daily_stat_persisted(
    persistence_provider: GarminDailyStatPersistenceProvider,
    stat_date: date,
    snapshot: GarminDailySnapshot,
) -> None:
    row = await persistence_provider.get_by_date(stat_date)
    assert row is not None
    assert row.Steps == snapshot.steps
    assert row.RestingHeartRate == snapshot.resting_heart_rate
    assert row.SleepSeconds == snapshot.sleep_seconds
    assert row.PeakBodyBattery == snapshot.peak_body_battery
    assert row.SleepScore == snapshot.sleep_score
    assert row.HrvLastNightAverage == snapshot.hrv_last_night_average
    assert row.HrvStatus == snapshot.hrv_status
    assert row.TrainingReadinessScore == snapshot.training_readiness_score
    assert row.TrainingStatus == snapshot.training_status
    assert row.Spo2Average == snapshot.spo2_average
    assert row.Vo2Max == snapshot.vo2_max
    assert row.FitnessAge == snapshot.fitness_age
    assert row.WeightGrams == snapshot.weight_grams
    assert row.IntensityMinutes == snapshot.intensity_minutes


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
