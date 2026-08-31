from datetime import date, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import EmailStr, Field, model_validator

from .base import ApiModel


class AuthenticateGarminRequest(ApiModel):
    email: EmailStr = Field(..., description="Garmin Connect account email.")
    password: str = Field(..., min_length=1, description="Garmin Connect account password.")


class GarminAuthenticateResponse(ApiModel):
    status: Literal["authenticated", "mfa_required"]
    mfa_session_id: UUID | None = Field(
        None, description="Set only when status is mfa_required; submit to /garmin/authenticate/mfa"
    )


class GarminSessionResponse(ApiModel):
    status: Literal["authenticated", "unauthenticated"]
    authenticated_at: datetime | None = Field(
        None, description="Set only when status is authenticated; the session's last-updated time."
    )


class SubmitGarminMfaRequest(ApiModel):
    mfa_session_id: UUID
    code: str = Field(..., min_length=1, description="MFA code sent by Garmin Connect.")


class UpsertGarminDailyStatRequest(ApiModel):
    stat_date: date = Field(..., description="The date to pull and store Garmin summary stats for.")


class BatchUpsertGarminDailyStatsRequest(ApiModel):
    start_date: date = Field(..., description="First date (inclusive) to pull and store stats for.")
    end_date: date = Field(..., description="Last date (inclusive) to pull and store stats for.")

    @model_validator(mode="after")
    def check_end_date_not_before_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class BatchUpsertGarminDailyStatsResponse(ApiModel):
    failed_dates: list[date] = Field(
        ..., description="Dates in the range that failed to upsert; empty if all succeeded."
    )


class GarminDailyStatResponse(ApiModel):
    stat_date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    peak_body_battery: int | None
    sleep_score: int | None
    hrv_last_night_average: int | None
    hrv_status: str | None
    training_readiness_score: int | None
    training_status: str | None
    vo2_max: float | None
    fitness_age: float | None
    weight_grams: int | None
    intensity_minutes: int | None
    updated_timestamp: datetime
