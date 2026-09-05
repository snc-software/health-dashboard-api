from datetime import datetime

from pydantic import Field

from .base import ApiModel


class StravaSessionResponse(ApiModel):
    connected: bool
    athlete_id: int | None = Field(
        None, description="Set only when connected; the Strava athlete id from the stored token."
    )
    updated_timestamp: datetime | None = Field(
        None, description="Set only when connected; when the stored token was last written."
    )
