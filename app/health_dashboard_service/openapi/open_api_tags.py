from enum import Enum

GARMIN: list[str | Enum] = ["Garmin"]
HEALTH: list[str | Enum] = ["Health"]
HEALTH_STATS: list[str | Enum] = ["Health Stats"]
STRAVA: list[str | Enum] = ["Strava"]

ALL_TAGS: list[dict[str, str]] = [
    {"name": "Garmin", "description": "Garmin Connect authentication and daily stats sync"},
    {"name": "Health", "description": "Liveness and readiness probes"},
    {"name": "Health Stats", "description": "Read-only access to stored daily health stats"},
    {"name": "Strava", "description": "Strava OAuth authentication"},
]
