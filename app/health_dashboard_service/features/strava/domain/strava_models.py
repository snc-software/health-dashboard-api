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
