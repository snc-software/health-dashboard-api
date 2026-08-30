from dataclasses import dataclass
from datetime import date, datetime
from typing import Final
from uuid import UUID

GARMIN_TOKEN_SINGLETON_ID: Final[UUID] = UUID("00000000-0000-0000-0000-000000000001")
"""Single-tenant service: one Garmin session, upserted by this fixed id."""


@dataclass(frozen=True, slots=True)
class GarminToken:
    Id: UUID
    TokenData: str
    CreatedTimestamp: datetime
    UpdatedTimestamp: datetime


@dataclass(frozen=True, slots=True)
class GarminDailyStat:
    Id: UUID
    StatDate: date
    Steps: int | None
    RestingHeartRate: int | None
    SleepSeconds: int | None
    PeakBodyBattery: int | None
    SleepScore: int | None
    HrvLastNightAverage: int | None
    HrvStatus: str | None
    TrainingReadinessScore: int | None
    TrainingStatus: str | None
    Vo2Max: float | None
    FitnessAge: float | None
    WeightGrams: int | None
    IntensityMinutes: int | None
    UpdatedTimestamp: datetime
