from typing import Any

from pydantic import Field

from .base import ApiModel


class ProblemDetails(ApiModel):
    """RFC 7807-style error body. Every non-2xx response uses this shape."""

    title: str = Field(..., description="A short, human-readable summary of the problem.")
    status: int = Field(..., description="The HTTP status code.")
    detail: str | None = Field(
        None, description="A human-readable explanation specific to this occurrence."
    )


class ValidationProblemDetails(ProblemDetails):
    """Returned for 400s; `extensions.errors` carries the per-field failures."""

    extensions: dict[str, Any] | None = Field(
        None, description="Additional fields providing more context about the error."
    )
