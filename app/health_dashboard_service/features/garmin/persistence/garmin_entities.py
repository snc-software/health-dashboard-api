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
    BodyBattery: int | None
    UpdatedTimestamp: datetime
