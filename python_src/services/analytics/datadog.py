"""Datadog analytics shim that records events locally."""

from __future__ import annotations

import time
from typing import Any

_INITIALIZED = False
_EVENTS: list[dict[str, Any]] = []


async def initializeDatadog(config: dict[str, Any] | None = None) -> dict[str, Any]:
    global _INITIALIZED
    _INITIALIZED = True
    return {"initialized": True, "config": dict(config or {})}


async def shutdownDatadog() -> dict[str, Any]:
    global _INITIALIZED
    _INITIALIZED = False
    return {"initialized": False, "events": len(_EVENTS)}


async def trackDatadogEvent(name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    if not _INITIALIZED:
        await initializeDatadog()
    event = {"name": name, "metadata": metadata or {}, "timestamp": time.time()}
    _EVENTS.append(event)
    return event


async def getDatadogEvents() -> list[dict[str, Any]]:
    return list(_EVENTS)
