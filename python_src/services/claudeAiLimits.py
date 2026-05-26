"""Quota status helpers for DeepSeek-compatible rate limit state.

The filename preserves the upstream module boundary, but the behavior now
understands OpenAI/DeepSeek-style rate-limit headers and errors.
"""

from __future__ import annotations

import time
from typing import Any, Callable

statusListeners: list[Callable[[dict[str, Any]], Any]] = []
_LAST_STATUS: dict[str, Any] = {"limited": False, "remaining": None, "reset_at": None, "updated_at": None}


def _header(headers: dict[str, Any], *names: str) -> Any:
    lowered = {str(k).lower(): v for k, v in (headers or {}).items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


async def getRateLimitDisplayName(limit_name: str | None = None) -> str:
    names = {
        "requests": "request quota",
        "tokens": "token quota",
        "input_tokens": "input token quota",
        "output_tokens": "output token quota",
    }
    return names.get(str(limit_name or "").lower(), str(limit_name or "quota"))


async def extractQuotaStatusFromHeaders(headers: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = headers or {}
    remaining = _header(headers, "x-ratelimit-remaining-requests", "x-ratelimit-remaining", "x-ratelimit-remaining-tokens")
    reset_at = _header(headers, "x-ratelimit-reset-requests", "x-ratelimit-reset", "retry-after")
    limit = _header(headers, "x-ratelimit-limit-requests", "x-ratelimit-limit", "x-ratelimit-limit-tokens")
    try:
        remaining_int = int(float(remaining)) if remaining is not None else None
    except ValueError:
        remaining_int = None
    status = {
        "limited": remaining_int is not None and remaining_int <= 0,
        "remaining": remaining_int,
        "limit": int(float(limit)) if limit is not None and str(limit).replace(".", "", 1).isdigit() else limit,
        "reset_at": reset_at,
        "updated_at": time.time(),
    }
    return status


async def extractQuotaStatusFromError(error: Any) -> dict[str, Any]:
    status = error.get("status") if isinstance(error, dict) else getattr(error, "status", None)
    message = error.get("message", "") if isinstance(error, dict) else str(error)
    limited = status == 429 or "rate limit" in str(message).lower() or "quota" in str(message).lower()
    return {"limited": limited, "status": status, "message": str(message), "updated_at": time.time()}


async def emitStatusChange(status: dict[str, Any]) -> dict[str, Any]:
    global _LAST_STATUS
    _LAST_STATUS = {**_LAST_STATUS, **status, "updated_at": time.time()}
    for listener in list(statusListeners):
        result = listener(dict(_LAST_STATUS))
        if hasattr(result, "__await__"):
            await result
    return dict(_LAST_STATUS)


async def checkQuotaStatus(headers: dict[str, Any] | None = None, error: Any = None) -> dict[str, Any]:
    if error is not None:
        status = await extractQuotaStatusFromError(error)
    else:
        status = await extractQuotaStatusFromHeaders(headers or {})
    return await emitStatusChange(status)


async def getRawUtilization() -> dict[str, Any]:
    return dict(_LAST_STATUS)
