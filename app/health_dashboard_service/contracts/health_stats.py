from datetime import date, datetime
from typing import Self

from pydantic import Field, model_validator

from .base import ApiModel


class GetDailyHealthStatsRequest(ApiModel):
    start_date: date = Field(..., description="First date (inclusive) to fetch stored stats for.")
    end_date: date = Field(..., description="Last date (inclusive) to fetch stored stats for.")

    @model_validator(mode="after")
    def check_end_date_not_before_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class DailyHealthStatResponse(ApiModel):
    date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    sleep_score: int | None
    peak_body_battery: int | None
    hrv_last_night_average: int | None
    hrv_status: str | None
    training_readiness_score: int | None
    training_status: str | None
    vo2_max: float | None
    fitness_age: float | None
    weight_grams: int | None
    intensity_minutes: int | None
    updated_timestamp: datetime
