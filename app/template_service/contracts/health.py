from .base import ApiModel


class HealthResponse(ApiModel):
    """Liveness probe response."""

    status: str
    service: str
    version: str


class ReadinessResponse(ApiModel):
    """Readiness probe response."""

    status: str
    database: str
