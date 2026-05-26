"""Local API logging for DeepSeek-compatible requests."""

from __future__ import annotations

import time
from typing import Any

from .errorUtils import formatAPIError

_API_LOG: list[dict[str, Any]] = []


async def logAPIQuery(model: str | None = None, endpoint: str | None = None, **metadata: Any) -> dict[str, Any]:
    event = {
        "type": "query",
        "model": model,
        "endpoint": endpoint,
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _API_LOG.append(event)
    return event


async def logAPIError(error: Any, **metadata: Any) -> dict[str, Any]:
    event = {
        "type": "error",
        "error": await formatAPIError(error),
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _API_LOG.append(event)
    return event


async def logAPISuccessAndDuration(duration_ms: float | int, **metadata: Any) -> dict[str, Any]:
    event = {
        "type": "success",
        "duration_ms": float(duration_ms),
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _API_LOG.append(event)
    return event


async def getAPILog() -> list[dict[str, Any]]:
    return list(_API_LOG)


async def clearAPILog() -> None:
    _API_LOG.clear()

