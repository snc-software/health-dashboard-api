from enum import Enum

TEMPLATES: list[str | Enum] = ["Templates"]
HEALTH: list[str | Enum] = ["Health"]

ALL_TAGS: list[dict[str, str]] = [
    {"name": "Templates", "description": "Template CRUD operations"},
    {"name": "Health", "description": "Liveness and readiness probes"},
]
