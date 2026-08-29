from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TemplateModel:
    id: UUID
    name: str
    created_timestamp: datetime
    updated_timestamp: datetime
