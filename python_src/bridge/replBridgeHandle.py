"""Process-global REPL bridge handle pointer."""

from __future__ import annotations

from typing import Any

from .sessionIdCompat import toCompatSessionId

_handle: Any | None = None


def setReplBridgeHandle(h: Any | None) -> None:
    global _handle
    _handle = h


def getReplBridgeHandle() -> Any | None:
    return _handle


def getSelfBridgeCompatId() -> str | None:
    handle = getReplBridgeHandle()
    if handle is None:
        return None
    session_id = getattr(handle, "bridgeSessionId", None)
    if session_id is None and isinstance(handle, dict):
        session_id = handle.get("bridgeSessionId")
    return toCompatSessionId(session_id) if isinstance(session_id, str) else None
