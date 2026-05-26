"""Local analytics event bus used by the migrated Python runtime."""

from __future__ import annotations

import copy
import time
from collections.abc import Callable
from typing import Any

from .config import isAnalyticsDisabled

AnalyticsSink = Callable[[dict[str, Any]], Any]

_SINKS: list[AnalyticsSink] = []
_EVENTS: list[dict[str, Any]] = []


async def _resetForTesting() -> None:
    _SINKS.clear()
    _EVENTS.clear()


async def attachAnalyticsSink(sink: AnalyticsSink) -> dict[str, Any]:
    """Attach a callable sink and return a detachable handle."""

    _SINKS.append(sink)

    async def detach() -> None:
        if sink in _SINKS:
            _SINKS.remove(sink)

    return {"detach": detach, "sink_count": len(_SINKS)}


def _strip(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): _strip(v)
            for k, v in value.items()
            if not str(k).startswith("__") and str(k) not in {"prototype", "constructor"}
        }
    if isinstance(value, list):
        return [_strip(item) for item in value]
    return value


async def stripProtoFields(payload: Any) -> Any:
    """Remove prototype-like keys before analytics storage/export."""

    return _strip(copy.deepcopy(payload))


async def logEvent(event_name: str, metadata: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any] | None:
    """Record an event locally and forward it to attached sinks."""

    config = kwargs.pop("config", None)
    if await isAnalyticsDisabled(config):
        return None
    payload = {
        "event": event_name,
        "metadata": await stripProtoFields(metadata or {}),
        "timestamp": kwargs.pop("timestamp", time.time()),
    }
    if kwargs:
        payload["extra"] = await stripProtoFields(kwargs)
    _EVENTS.append(payload)
    for sink in list(_SINKS):
        result = sink(payload)
        if hasattr(result, "__await__"):
            await result
    return payload


async def logEventAsync(event_name: str, metadata: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any] | None:
    """Async alias kept for TypeScript API compatibility."""

    return await logEvent(event_name, metadata, **kwargs)


async def getLoggedEvents() -> list[dict[str, Any]]:
    """Return a copy of in-memory events for tests and local diagnostics."""

    return copy.deepcopy(_EVENTS)
