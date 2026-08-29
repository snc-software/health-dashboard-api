import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ...contracts.common import ProblemDetails, ValidationProblemDetails

logger = logging.getLogger(__name__)

_TITLES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error",
}


def _problem_response(problem: ProblemDetails, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json", by_alias=True, exclude_none=True),
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Render HTTPException as ProblemDetails."""
    return _problem_response(
        ProblemDetails(
            title=_TITLES.get(exc.status_code, "Error"),
            status=exc.status_code,
            detail=str(exc.detail) if exc.detail else None,
        ),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render request-validation failures as a 400 ValidationProblemDetails."""
    errors = [
        {
            "location": list(error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        for error in exc.errors()
    ]

    return _problem_response(
        ValidationProblemDetails(
            title=_TITLES[status.HTTP_400_BAD_REQUEST],
            status=status.HTTP_400_BAD_REQUEST,
            detail="The request failed validation.",
            extensions={"errors": errors},
        )
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log the traceback and return an opaque 500."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)

    return _problem_response(
        ProblemDetails(
            title=_TITLES[status.HTTP_500_INTERNAL_SERVER_ERROR],
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
