from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GarminCredentialsModel:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class GarminAuthenticationResultModel:
    status: Literal["authenticated", "mfa_required"]
    mfa_session_id: UUID | None


@dataclass(frozen=True, slots=True)
class GarminMfaSubmissionModel:
    mfa_session_id: UUID
    code: str


@dataclass(frozen=True, slots=True)
class GarminTokenModel:
    id: UUID
    token_data: str
    created_timestamp: datetime
    updated_timestamp: datetime


@dataclass(frozen=True, slots=True)
class GarminDailyStatModel:
    id: UUID
    stat_date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    body_battery: int | None
    updated_timestamp: datetime
