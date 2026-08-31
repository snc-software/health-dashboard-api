"""Step implementations for the get-daily-health-stats service test."""

from datetime import UTC, date, datetime
from uuid import uuid7

import httpx

from health_dashboard_service.features.garmin.persistence.garmin_entities import GarminDailyStat
from tests.persistence_providers.garmin_daily_stat_persistence_provider import (
    GarminDailyStatPersistenceProvider,
)
from tests.service.infrastructure.clients.health_stats_client import (
    get_daily_health_stats as _call,
)


async def get_daily_health_stats(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    return await _call(client, start_date, end_date)


async def a_daily_stat_is_stored(
    persistence_provider: GarminDailyStatPersistenceProvider,
    stat_date: date,
    **overrides: object,
) -> GarminDailyStat:
    fields: dict[str, object] = {
        "Id": uuid7(),
        "StatDate": stat_date,
        "Steps": 8500,
        "RestingHeartRate": 52,
        "SleepSeconds": 25200,
        "PeakBodyBattery": 68,
        "SleepScore": 85,
        "HrvLastNightAverage": 45,
        "HrvStatus": "BALANCED",
        "TrainingReadinessScore": 72,
        "TrainingStatus": "PRODUCTIVE",
        "Vo2Max": 45.0,
        "FitnessAge": 32.5,
        "WeightGrams": 70500,
        "IntensityMinutes": 35,
        "UpdatedTimestamp": datetime.now(UTC),
    }
    fields.update(overrides)
    stat = GarminDailyStat(**fields)  # type: ignore[arg-type]
    await persistence_provider.insert(stat)
    return stat


def assert_response_status(response: httpx.Response, status_code: int) -> None:
    assert response.status_code == status_code
