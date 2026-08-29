"""Client wrapper for calling this service's own /garmin/* endpoints from tests."""

from datetime import date

import httpx

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    SubmitGarminMfaRequest,
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


async def refresh_garmin_data(
    client: httpx.AsyncClient, stat_date: date | None = None
) -> httpx.Response:
    params = {"stat_date": stat_date.isoformat()} if stat_date else None
    req = BaseApiClient.get_base_request(client, "POST", "/garmin/refresh", params=params)
    return await client.send(req)
