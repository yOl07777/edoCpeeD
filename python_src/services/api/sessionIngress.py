"""Local session ingress store used by the migrated runtime."""

from __future__ import annotations

import time
from typing import Any

_SESSIONS: dict[str, list[dict[str, Any]]] = {}
_TELEPORT_EVENTS: list[dict[str, Any]] = []


async def appendSessionLog(session_id: str, event: dict[str, Any] | str, **metadata: Any) -> dict[str, Any]:
    entry = {
        "session_id": session_id,
        "event": event if isinstance(event, dict) else {"message": str(event)},
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _SESSIONS.setdefault(session_id, []).append(entry)
    if metadata.get("teleport"):
        _TELEPORT_EVENTS.append(entry)
    return entry


async def getSessionLogs(session_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    if session_id is None:
        logs = [entry for entries in _SESSIONS.values() for entry in entries]
    else:
        logs = list(_SESSIONS.get(session_id, []))
    logs = sorted(logs, key=lambda item: item["timestamp"])
    return logs[-limit:] if limit else logs


async def getSessionLogsViaOAuth(session_id: str | None = None, **_kwargs: Any) -> list[dict[str, Any]]:
    """OAuth variant kept for compatibility; local migration uses the same store."""

    return await getSessionLogs(session_id)


async def clearSession(session_id: str) -> dict[str, Any]:
    removed = len(_SESSIONS.pop(session_id, []))
    return {"session_id": session_id, "removed": removed}


async def clearAllSessions() -> dict[str, Any]:
    count = sum(len(entries) for entries in _SESSIONS.values())
    _SESSIONS.clear()
    _TELEPORT_EVENTS.clear()
    return {"removed": count}


async def getTeleportEvents(limit: int | None = None) -> list[dict[str, Any]]:
    return list(_TELEPORT_EVENTS[-limit:] if limit else _TELEPORT_EVENTS)

