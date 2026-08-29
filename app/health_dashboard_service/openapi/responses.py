from typing import Any

from ..contracts.common import ProblemDetails, ValidationProblemDetails

Responses = dict[int | str, dict[str, Any]]

BAD_REQUEST: Responses = {
    400: {"model": ValidationProblemDetails, "description": "Request validation failed"}
}

NOT_FOUND: Responses = {404: {"model": ProblemDetails, "description": "Resource not found"}}

SERVER_ERROR: Responses = {500: {"model": ProblemDetails, "description": "Internal server error"}}

SERVICE_UNAVAILABLE: Responses = {
    503: {"model": ProblemDetails, "description": "Dependency unavailable"}
}
