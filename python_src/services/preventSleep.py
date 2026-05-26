"""Local prevent-sleep state.

The desktop TypeScript runtime may call OS APIs. The Python migration keeps a
deterministic in-process lease instead.
"""

from __future__ import annotations

import time
from typing import Any

_LEASE: dict[str, Any] | None = None


async def startPreventSleep(reason: str = "deepseek-code-running") -> dict[str, Any]:
    global _LEASE
    if _LEASE is None:
        _LEASE = {"active": True, "reason": reason, "started_at": time.time(), "ref_count": 1}
    else:
        _LEASE["active"] = True
        _LEASE["ref_count"] = int(_LEASE.get("ref_count", 0)) + 1
        _LEASE["reason"] = reason or _LEASE.get("reason")
    return dict(_LEASE)


async def stopPreventSleep() -> dict[str, Any]:
    global _LEASE
    if _LEASE is None:
        return {"active": False, "ref_count": 0}
    _LEASE["ref_count"] = max(0, int(_LEASE.get("ref_count", 1)) - 1)
    if _LEASE["ref_count"] == 0:
        _LEASE["active"] = False
    return dict(_LEASE)


async def forceStopPreventSleep() -> dict[str, Any]:
    global _LEASE
    _LEASE = {"active": False, "ref_count": 0, "stopped_at": time.time()}
    return dict(_LEASE)


async def getPreventSleepState() -> dict[str, Any]:
    return dict(_LEASE or {"active": False, "ref_count": 0})
