"""Mocks Strava's OAuth HTTP endpoints for service tests, via `respx` (per
service-test-standards.md's rule that external API interaction must be mocked
using respx; Strava's client is plain `httpx`, so Garmin's SDK-mocking deviation
doesn't apply here).
"""

import respx
from httpx import Response

_TOKEN_URL = "https://www.strava.com/oauth/token"
_ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def configure_successful_token_exchange(
    respx_mock: respx.MockRouter,
    *,
    access_token: str,
    refresh_token: str,
    expires_at: int,
    athlete_id: int,
    scope: str = "read,activity:read_all",
) -> None:
    respx_mock.post(_TOKEN_URL).mock(
        return_value=Response(
            200,
            json={
                "token_type": "Bearer",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "expires_in": 21600,
                "athlete": {"id": athlete_id},
                "scope": scope,
            },
        )
    )


def configure_token_exchange_rejected(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(_TOKEN_URL).mock(return_value=Response(400, json={"message": "Bad Request"}))


def configure_token_exchange_unreachable(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(_TOKEN_URL).mock(
        return_value=Response(500, json={"message": "Internal Server Error"})
    )


def configure_successful_athlete_verification(
    respx_mock: respx.MockRouter, *, athlete_id: int
) -> None:
    respx_mock.get(_ATHLETE_URL).mock(return_value=Response(200, json={"id": athlete_id}))


def configure_athlete_verification_rejected(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(_ATHLETE_URL).mock(return_value=Response(401, json={"message": "Unauthorized"}))


def configure_athlete_verification_unreachable(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(_ATHLETE_URL).mock(
        return_value=Response(500, json={"message": "Internal Server Error"})
    )


def configure_successful_token_refresh(
    respx_mock: respx.MockRouter, *, access_token: str, refresh_token: str, expires_at: int
) -> None:
    respx_mock.post(_TOKEN_URL).mock(
        return_value=Response(
            200,
            json={
                "token_type": "Bearer",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "expires_in": 21600,
            },
        )
    )


def configure_token_refresh_rejected(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(_TOKEN_URL).mock(return_value=Response(400, json={"message": "Bad Request"}))


def configure_successful_activities_list(
    respx_mock: respx.MockRouter, activities: list[dict]
) -> None:
    respx_mock.get(_ACTIVITIES_URL).mock(return_value=Response(200, json=activities))


def configure_activities_list_rejected(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(_ACTIVITIES_URL).mock(
        return_value=Response(401, json={"message": "Unauthorized"})
    )


def configure_activities_list_unreachable(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(_ACTIVITIES_URL).mock(
        return_value=Response(500, json={"message": "Internal Server Error"})
    )


def configure_activities_list_sequence(
    respx_mock: respx.MockRouter, responses: list[list[dict]]
) -> None:
    """Returns each list of activities in order across successive calls, so a test can prove
    a second sync with different field values overwrites the first."""
    route = respx_mock.get(_ACTIVITIES_URL)
    route.side_effect = [Response(200, json=activities) for activities in responses]


def configure_activities_list_for_access_token(
    respx_mock: respx.MockRouter, *, access_token: str, activities: list[dict]
) -> None:
    """Matches only requests carrying the given bearer token, so a test can prove which
    token (e.g. before vs. after a refresh) was actually used to call Strava."""
    respx_mock.get(_ACTIVITIES_URL, headers={"Authorization": f"Bearer {access_token}"}).mock(
        return_value=Response(200, json=activities)
    )
