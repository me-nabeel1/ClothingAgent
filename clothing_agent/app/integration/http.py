"""Small asynchronous HTTP transport used by the commerce adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from .errors import CommerceHTTPError, CommerceTransportError


class AsyncJSONTransport:
    """Execute JSON HTTP requests and convert transport failures into domain errors."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 15.0, client: httpx.AsyncClient | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "AsyncJSONTransport":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout_seconds)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ) -> Any:
        """Send one HTTP request and return decoded JSON or an empty body.

        No domain decisions are made here. The transport only handles URL
        construction, HTTP execution and conversion of network failures into
        deterministic commerce-client exceptions.
        """

        client = self._client
        if client is None:
            client = httpx.AsyncClient(timeout=self._timeout_seconds)
            temporary_client = True
        else:
            temporary_client = False

        try:
            try:
                response = await client.request(method, f"{self._base_url}{path}", params=params, json=json)
            except httpx.HTTPError as exc:
                raise CommerceTransportError(f"Unable to reach commerce API: {exc}") from exc

            if response.status_code >= 400:
                try:
                    body: object = response.json()
                except ValueError:
                    body = response.text
                raise CommerceHTTPError(
                    response.status_code,
                    "request was rejected",
                    response_body=body,
                )

            if not response.content:
                return None

            try:
                return response.json()
            except ValueError as exc:
                raise CommerceHTTPError(
                    response.status_code,
                    "response was not valid JSON",
                    response_body=response.text,
                ) from exc
        finally:
            if temporary_client:
                await client.aclose()
