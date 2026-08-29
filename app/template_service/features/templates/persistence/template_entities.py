from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Template:
    Id: UUID
    Name: str
    CreatedTimestamp: datetime
    UpdatedTimestamp: datetime
    Deleted: bool
