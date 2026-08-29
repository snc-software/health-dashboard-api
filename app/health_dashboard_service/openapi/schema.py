from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

_AUTO_VALIDATION_SCHEMAS = ("HTTPValidationError", "ValidationError")


def configure_openapi(app: FastAPI) -> None:
    """
    Install a schema builder that drops FastAPI's automatic 422 responses.

    Validation failures are returned as 400 by the exception handlers, so the
    generated 422 entries would document a status the service never sends.
    """

    def openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )

        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation.get("responses", {}).pop("422", None)

        schemas = schema.get("components", {}).get("schemas", {})
        for name in _AUTO_VALIDATION_SCHEMAS:
            schemas.pop(name, None)

        app.openapi_schema = schema
        return schema

    app.openapi = openapi  # type: ignore[method-assign]
