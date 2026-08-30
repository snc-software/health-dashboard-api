"""Step implementations for the batch-upsert-Garmin-daily-stats service test."""

from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid7

import httpx
from pytest_mock import MockerFixture

from health_dashboard_service.contracts.garmin import BatchUpsertGarminDailyStatsRequest
from health_dashboard_service.features.garmin.persistence.garmin_entities import GarminDailyStat
from health_dashboard_service.infrastructure.garmin import garmin_client_factory
from health_dashboard_service.infrastructure.garmin.garmin_client_factory import (
    GarminDailySnapshot,
)
from tests.persistence_providers.garmin_daily_stat_persistence_provider import (
    GarminDailyStatPersistenceProvider,
)
from tests.service.infrastructure.clients.garmin_client import (
    batch_upsert_garmin_daily_stats as _call,
)
from tests.service.infrastructure.mocks import garmin_api_mock


async def batch_upsert_garmin_daily_stats(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    return await _call(
        client, BatchUpsertGarminDailyStatsRequest(start_date=start_date, end_date=end_date)
    )


async def batch_upsert_garmin_daily_stats_with_unvalidated_range(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    """Bypasses the contract's own model_validator so an invalid range still reaches the
    server, in order to exercise the endpoint's 400 response."""
    request = BatchUpsertGarminDailyStatsRequest.model_construct(
        start_date=start_date, end_date=end_date
    )
    return await _call(client, request)


def garmin_returns_daily_stats(
    mocker: MockerFixture, snapshots_by_date: dict[date, GarminDailySnapshot]
) -> None:
    garmin_api_mock.configure_daily_snapshots(mocker, snapshots_by_date)


def spy_on_fetch_daily_snapshot(mocker: MockerFixture) -> Any:
    return mocker.patch.object(garmin_client_factory, "fetch_daily_snapshot")


def garmin_fails_for_some_dates(
    mocker: MockerFixture,
    snapshots_by_date: dict[date, GarminDailySnapshot],
    failing_dates: set[date],
) -> None:
    garmin_api_mock.configure_daily_snapshots_with_failure(mocker, snapshots_by_date, failing_dates)


async def a_daily_stat_is_already_stored(
    persistence_provider: GarminDailyStatPersistenceProvider, stat_date: date
) -> None:
    now = datetime.now(UTC)
    await persistence_provider.insert(
        GarminDailyStat(
            Id=uuid7(),
            StatDate=stat_date,
            Steps=1,
            RestingHeartRate=1,
            SleepSeconds=1,
            PeakBodyBattery=1,
            SleepScore=1,
            HrvLastNightAverage=1,
            HrvStatus="stale",
            TrainingReadinessScore=1,
            TrainingStatus="stale",
            Vo2Max=1.0,
            FitnessAge=1.0,
            WeightGrams=1,
            IntensityMinutes=1,
            UpdatedTimestamp=now,
        )
    )


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
    assert row.Vo2Max == snapshot.vo2_max
    assert row.FitnessAge == snapshot.fitness_age
    assert row.WeightGrams == snapshot.weight_grams
    assert row.IntensityMinutes == snapshot.intensity_minutes


async def assert_no_daily_stat_persisted(
    persistence_provider: GarminDailyStatPersistenceProvider, stat_date: date
) -> None:
    assert await persistence_provider.get_by_date(stat_date) is None


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
