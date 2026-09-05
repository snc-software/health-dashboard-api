from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StravaTokenModel:
    id: UUID
    access_token: str
    refresh_token: str
    expires_at: datetime
    athlete_id: int
    scope: str
    created_timestamp: datetime
    updated_timestamp: datetime


@dataclass(frozen=True, slots=True)
class StravaSessionStatusModel:
    connected: bool
    athlete_id: int | None
    updated_timestamp: datetime | None


@dataclass(frozen=True, slots=True)
class StravaActivityModel:
    id: UUID
    strava_activity_id: int
    name: str
    type: str
    sport_type: str
    start_date: datetime
    start_date_local: datetime
    distance_metres: float
    moving_time_seconds: int
    elapsed_time_seconds: int
    total_elevation_gain_metres: float
    average_heartrate: float | None
    max_heartrate: float | None
    gear_id: str | None
    updated_timestamp: datetime


@dataclass(frozen=True, slots=True)
class StravaActivityStatsModel:
    """Raw period aggregates, pre-pace. `StravaActivityPeriodStatsModel` is computed from
    this by the domain service, which divides `total_run_moving_time_seconds` by
    `total_run_distance_metres` to get pace."""

    total_activities: int
    total_run_distance_metres: float
    total_run_moving_time_seconds: int


@dataclass(frozen=True, slots=True)
class StravaActivityPeriodStatsModel:
    total_activities: int
    total_run_distance_metres: float
    average_run_pace_seconds_per_km: float | None


@dataclass(frozen=True, slots=True)
class StravaActivitySummaryModel:
    current_period: StravaActivityPeriodStatsModel
    prior_period: StravaActivityPeriodStatsModel
