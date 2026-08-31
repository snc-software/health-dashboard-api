"""Client wrapper for calling this service's own /start/{startDate}/end/{endDate}/health-stats endpoint from tests."""

from datetime import date

import httpx

from .base_api_client import BaseApiClient


async def get_daily_health_stats(
    client: httpx.AsyncClient, start_date: date, end_date: date
) -> httpx.Response:
    req = BaseApiClient.get_base_request(
        client,
        "GET",
        f"/start/{start_date.isoformat()}/end/{end_date.isoformat()}/health-stats",
    )
    return await client.send(req)
