"""Client wrapper for calling this service's own /strava/* endpoints from tests.

`api_client` never follows redirects (httpx's default), so the redirect-based
endpoints' `Location` header and status code can be asserted directly.
"""

import httpx

from .base_api_client import BaseApiClient


async def authorize_strava(client: httpx.AsyncClient) -> httpx.Response:
    req = BaseApiClient.get_base_request(client, "GET", "/authorize-strava")
    return await client.send(req)


async def strava_callback(
    client: httpx.AsyncClient,
    *,
    code: str | None = None,
    scope: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> httpx.Response:
    params = {
        key: value
        for key, value in {"code": code, "scope": scope, "state": state, "error": error}.items()
        if value is not None
    }
    req = BaseApiClient.get_base_request(client, "GET", "/strava-callback", params=params)
    return await client.send(req)


async def get_strava_session(client: httpx.AsyncClient) -> httpx.Response:
    req = BaseApiClient.get_base_request(client, "GET", "/strava-session")
    return await client.send(req)
