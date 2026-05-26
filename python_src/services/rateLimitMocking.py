"""Helpers that apply mock DeepSeek rate-limit behavior."""

from __future__ import annotations

from typing import Any

from .mockRateLimits import addExceededLimit, applyMockHeaders, getMockStatus, shouldProcessMockLimits
from .rateLimitMessages import getRateLimitErrorMessage, isRateLimitErrorMessage


async def shouldProcessRateLimits(config: dict[str, Any] | None = None) -> bool:
    if config and "processRateLimits" in config:
        return bool(config["processRateLimits"])
    return True


async def processRateLimitHeaders(headers: dict[str, Any] | None = None) -> dict[str, Any]:
    merged = await applyMockHeaders(headers or {})
    remaining = merged.get("x-ratelimit-remaining-requests") or merged.get("x-ratelimit-remaining")
    reset = merged.get("x-ratelimit-reset-requests") or merged.get("retry-after")
    limited = False
    try:
        limited = remaining is not None and int(float(remaining)) <= 0
    except ValueError:
        limited = False
    if limited:
        await addExceededLimit("requests", {"headers": merged})
    return {"headers": merged, "limited": limited, "remaining": remaining, "reset": reset}


async def isMockRateLimitError(error: Any) -> bool:
    status = error.get("status") if isinstance(error, dict) else getattr(error, "status", None)
    message = error.get("message", "") if isinstance(error, dict) else str(error)
    return status == 429 or await isRateLimitErrorMessage(str(message))


async def checkMockRateLimitError(error: Any = None, headers: dict[str, Any] | None = None) -> dict[str, Any]:
    status = await processRateLimitHeaders(headers or {})
    mock_status = await getMockStatus()
    limited = status["limited"] or bool(mock_status["exceeded"]) or (await isMockRateLimitError(error or {}))
    return {
        "limited": limited,
        "message": await getRateLimitErrorMessage(error or {}, status["headers"]) if limited else None,
        "status": status,
        "mock": mock_status,
        "enabled": await shouldProcessMockLimits(),
    }
