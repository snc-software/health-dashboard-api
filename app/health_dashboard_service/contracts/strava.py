from datetime import date, datetime
from typing import Self

from pydantic import Field, model_validator

from .base import ApiModel


class StravaSessionResponse(ApiModel):
    connected: bool
    athlete_id: int | None = Field(
        None, description="Set only when connected; the Strava athlete id from the stored token."
    )
    updated_timestamp: datetime | None = Field(
        None, description="Set only when connected; when the stored token was last written."
    )


class FetchStravaActivitiesRequest(ApiModel):
    start_date: date = Field(
        ..., description="First date (inclusive), in UTC, to fetch activities for."
    )
    end_date: date = Field(
        ..., description="Last date (inclusive), in UTC, to fetch activities for."
    )

    @model_validator(mode="after")
    def check_end_date_not_before_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class FetchStravaActivitiesResponse(ApiModel):
    counts_by_type: dict[str, int] = Field(
        ...,
        description=(
            "Count of activities synced by this call, keyed by Strava's type field "
            '(e.g. "Run", "WeightTraining", "Workout"). Reflects only the activities returned '
            "by this request's range, not the whole table."
        ),
    )


class GetStravaActivitiesRequest(ApiModel):
    start_date: date = Field(..., description="First date (inclusive) to fetch activities for.")
    end_date: date = Field(..., description="Last date (inclusive) to fetch activities for.")

    @model_validator(mode="after")
    def check_end_date_not_before_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class StravaActivityResponse(ApiModel):
    strava_activity_id: int = Field(..., description="Strava's own activity id.")
    name: str
    sport_type: str = Field(..., description="Strava's sport_type field.")
    start_date: datetime = Field(
        ..., description="UTC instant — the moment the activity started, in UTC."
    )
    start_date_local: datetime = Field(
        ...,
        description=(
            "The wall-clock time at the activity's location (e.g. a run started in Australia "
            "keeps its Australian local time here, not a UTC-shifted one)."
        ),
    )
    distance_metres: float
    moving_time_seconds: int
    elapsed_time_seconds: int
    total_elevation_gain_metres: float
    average_heartrate: float | None
    max_heartrate: float | None
    gear_id: str | None


class GetStravaActivitySummaryRequest(ApiModel):
    start_date: date = Field(..., description="First date (inclusive) of the period to summarise.")
    end_date: date = Field(..., description="Last date (inclusive) of the period to summarise.")

    @model_validator(mode="after")
    def check_end_date_not_before_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class StravaActivityPeriodStatsResponse(ApiModel):
    total_activities: int = Field(..., description="All activity types.")
    total_run_distance_metres: float = Field(..., description='sport_type == "Run" only.')
    average_run_pace_seconds_per_km: float | None = Field(
        None,
        description=(
            "sum(moving_time)/sum(distance_km) across runs in the period; "
            "None when the period has no runs."
        ),
    )


class StravaActivitySummaryResponse(ApiModel):
    current_period: StravaActivityPeriodStatsResponse
    prior_period: StravaActivityPeriodStatsResponse
