from dataclasses import dataclass
from datetime import datetime
from typing import Final
from uuid import UUID

STRAVA_TOKEN_SINGLETON_ID: Final[UUID] = UUID("00000000-0000-0000-0000-000000000002")
"""Single-tenant service: one Strava token, upserted by this fixed id."""


@dataclass(frozen=True, slots=True)
class StravaToken:
    Id: UUID
    AccessToken: str
    RefreshToken: str
    ExpiresAt: datetime
    AthleteId: int
    Scope: str
    CreatedTimestamp: datetime
    UpdatedTimestamp: datetime


@dataclass(frozen=True, slots=True)
class StravaActivity:
    Id: UUID
    StravaActivityId: int
    Name: str
    SportType: str
    StartDate: datetime
    StartDateLocal: datetime
    DistanceMetres: float
    MovingTimeSeconds: int
    ElapsedTimeSeconds: int
    TotalElevationGainMetres: float
    AverageHeartrate: float | None
    MaxHeartrate: float | None
    GearId: str | None
    UpdatedTimestamp: datetime


@dataclass(frozen=True, slots=True)
class StravaActivityStatsRow:
    TotalActivities: int
    TotalRunDistanceMetres: float
    TotalRunMovingTimeSeconds: int
