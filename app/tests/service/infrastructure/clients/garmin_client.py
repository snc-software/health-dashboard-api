"""Client wrapper for calling this service's own /garmin/* endpoints from tests."""

import httpx

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    SubmitGarminMfaRequest,
    UpsertGarminDailyStatRequest,
)

from .base_api_client import BaseApiClient


async def authenticate_garmin(
    client: httpx.AsyncClient, request: AuthenticateGarminRequest
) -> httpx.Response:
    req = BaseApiClient.get_base_request(
        client, "POST", "/garmin/authenticate", json=request.model_dump(by_alias=True)
    )
    return await client.send(req)


async def submit_garmin_mfa(
    client: httpx.AsyncClient, request: SubmitGarminMfaRequest
) -> httpx.Response:
    payload = request.model_dump(by_alias=True, mode="json")
    req = BaseApiClient.get_base_request(client, "POST", "/garmin/authenticate/mfa", json=payload)
    return await client.send(req)


async def upsert_garmin_daily_stat(
    client: httpx.AsyncClient, request: UpsertGarminDailyStatRequest
) -> httpx.Response:
    payload = request.model_dump(by_alias=True, mode="json")
    req = BaseApiClient.get_base_request(client, "POST", "/garmin-daily-stats", json=payload)
    return await client.send(req)
