from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field

from .base import ApiModel


class AuthenticateGarminRequest(ApiModel):
    email: EmailStr = Field(..., description="Garmin Connect account email.")
    password: str = Field(..., min_length=1, description="Garmin Connect account password.")


class GarminAuthenticateResponse(ApiModel):
    status: Literal["authenticated", "mfa_required"]
    mfa_session_id: UUID | None = Field(
        None, description="Set only when status is mfa_required; submit to /garmin/authenticate/mfa"
    )


class SubmitGarminMfaRequest(ApiModel):
    mfa_session_id: UUID
    code: str = Field(..., min_length=1, description="MFA code sent by Garmin Connect.")


class UpsertGarminDailyStatRequest(ApiModel):
    stat_date: date = Field(..., description="The date to pull and store Garmin summary stats for.")


class GarminDailyStatResponse(ApiModel):
    stat_date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    body_battery: int | None
    updated_timestamp: datetime
