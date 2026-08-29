from pydantic import BaseModel, Field

from .base import ApiModel

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


class Pagination(ApiModel):
    """Pagination details"""

    page: int
    """Page number returned"""

    size: int
    """Number of records in this page"""

    total: int
    """Total available records"""


class PagedResponse[T](ApiModel):
    """Generic paged response model"""

    items: list[T]
    """Returned items"""

    pagination: Pagination
    """Pagination details"""


class PaginationParameters(BaseModel):
    """Pagination parameters for requests, bound to query parameters."""

    page: int = Field(1, ge=1, description="Page number to retrieve, default 1")
    """Page number to retrieve, default 1"""

    page_size: int = Field(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"The maximum number of records to return (max {MAX_PAGE_SIZE})",
    )
    """The maximum number of records to return"""

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
