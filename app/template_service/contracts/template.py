from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base import ApiModel


class CreateTemplateRequest(ApiModel):
    name: str = Field(..., min_length=1, max_length=200)


class TemplateResponse(ApiModel):
    id: UUID
    name: str
    created_timestamp: datetime
    updated_timestamp: datetime
