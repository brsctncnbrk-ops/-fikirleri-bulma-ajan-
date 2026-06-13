"""HTTP helpers: a shared client with timeout and retry/backoff."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15.0
DEFAULT_RETRIES = 3
USER_AGENT = "trendidea/0.1 (+https://github.com/brsctncnbrk-ops)"


def request_json(
    url: str,
    *,
    client: httpx.Client | None = None,
    params: dict | None = None,
    headers: dict | None = None,
    retries: int = DEFAULT_RETRIES,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """GET a URL and return parsed JSON, retrying transient errors with backoff."""
    return _request(
        "GET",
        url,
        client=client,
        params=params,
        headers=headers,
        retries=retries,
        timeout=timeout,
        parse="json",
    )


def request_text(
    url: str,
    *,
    client: httpx.Client | None = None,
    params: dict | None = None,
    headers: dict | None = None,
    retries: int = DEFAULT_RETRIES,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """GET a URL and return the response body as text, with retry/backoff."""
    return _request(
        "GET",
        url,
        client=client,
        params=params,
        headers=headers,
        retries=retries,
        timeout=timeout,
        parse="text",
    )


def post_json(
    url: str,
    *,
    json_body: dict,
    client: httpx.Client | None = None,
    headers: dict | None = None,
    retries: int = DEFAULT_RETRIES,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """POST a JSON body and return parsed JSON, with retry/backoff."""
    return _request(
        "POST",
        url,
        client=client,
        headers=headers,
        json_body=json_body,
        retries=retries,
        timeout=timeout,
        parse="json",
    )


def _request(
    method: str,
    url: str,
    *,
    client: httpx.Client | None = None,
    params: dict | None = None,
    headers: dict | None = None,
    json_body: dict | None = None,
    retries: int = DEFAULT_RETRIES,
    timeout: float = DEFAULT_TIMEOUT,
    parse: str = "json",
) -> Any:
    owns_client = client is None
    client = client or httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT})
    merged_headers = {**({} if headers is None else headers)}
    try:
        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                resp = client.request(
                    method, url, params=params, headers=merged_headers, json=json_body
                )
                resp.raise_for_status()
                return resp.json() if parse == "json" else resp.text
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt == retries:
                    break
                backoff = 2 ** (attempt - 1)
                logger.warning(
                    "http retry",
                    extra={"url": url, "attempt": attempt, "backoff_s": backoff},
                )
                time.sleep(backoff)
        raise last_exc  # type: ignore[misc]
    finally:
        if owns_client:
            client.close()
