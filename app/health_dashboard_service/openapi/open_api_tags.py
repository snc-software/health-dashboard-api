from enum import Enum

GARMIN: list[str | Enum] = ["Garmin"]
HEALTH: list[str | Enum] = ["Health"]

ALL_TAGS: list[dict[str, str]] = [
    {"name": "Garmin", "description": "Garmin Connect authentication and daily stats sync"},
    {"name": "Health", "description": "Liveness and readiness probes"},
]
