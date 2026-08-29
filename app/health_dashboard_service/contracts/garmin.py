from datetime import date, datetime

from pydantic import EmailStr, Field

from .base import ApiModel


class AuthenticateGarminRequest(ApiModel):
    email: EmailStr = Field(..., description="Garmin Connect account email.")
    password: str = Field(..., min_length=1, description="Garmin Connect account password.")


class GarminDailyStatResponse(ApiModel):
    stat_date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    body_battery: int | None
    updated_timestamp: datetime
