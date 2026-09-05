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
