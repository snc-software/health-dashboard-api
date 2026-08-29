"""Shared request-building helper for service-test API client wrappers."""

from typing import Any

import httpx


class BaseApiClient:
    @staticmethod
    def get_base_request(
        client: httpx.AsyncClient, method: str, url: str, **kwargs: Any
    ) -> httpx.Request:
        return client.build_request(method, url, **kwargs)
