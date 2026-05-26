"""Dry-run team memory watcher state."""

from __future__ import annotations

from typing import Any

from .index import createSyncState, pushTeamMemory

_state: dict[str, Any] = {"started": False, "pendingWrites": 0, "suppressedReason": None, "syncState": None}


async def isPermanentFailure(*args: Any, **kwargs: Any) -> bool:
    result = kwargs.get("result") if "result" in kwargs else (args[0] if args else {})
    if not isinstance(result, dict):
        return False
    if result.get("errorType") in {"no_oauth", "no_repo"}:
        return True
    status = result.get("httpStatus")
    return isinstance(status, int) and 400 <= status < 500 and status not in {409, 429}


async def _resetWatcherStateForTesting(*args: Any, **kwargs: Any) -> None:
    _state.update({"started": False, "pendingWrites": 0, "suppressedReason": None, "syncState": None})


async def startTeamMemoryWatcher(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if _state["syncState"] is None:
        _state["syncState"] = await createSyncState()
    _state["started"] = True
    return {"started": True, "pendingWrites": _state["pendingWrites"]}


async def stopTeamMemoryWatcher(*args: Any, **kwargs: Any) -> dict[str, Any]:
    was_started = bool(_state["started"])
    _state["started"] = False
    return {"stopped": was_started}


async def notifyTeamMemoryWrite(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if _state["suppressedReason"] is not None:
        return {"scheduled": False, "suppressedReason": _state["suppressedReason"]}
    _state["pendingWrites"] += 1
    if kwargs.get("pushNow"):
        result = await pushTeamMemory(_state["syncState"] or await createSyncState())
        if not result.get("success") and await isPermanentFailure(result):
            _state["suppressedReason"] = result.get("errorType") or result.get("httpStatus") or "unknown"
        else:
            _state["pendingWrites"] = 0
        return {"scheduled": True, "pushed": result}
    return {"scheduled": True, "pendingWrites": _state["pendingWrites"]}


async def _startFileWatcherForTesting(*args: Any, **kwargs: Any) -> dict[str, Any]:
    path = str(kwargs.get("path") or (args[0] if args else ""))
    await startTeamMemoryWatcher()
    return {"started": True, "path": path}


__all__ = [
    "_resetWatcherStateForTesting",
    "_startFileWatcherForTesting",
    "isPermanentFailure",
    "notifyTeamMemoryWrite",
    "startTeamMemoryWatcher",
    "stopTeamMemoryWatcher",
]
