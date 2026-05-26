from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useRemoteSession(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    session_id = pick(options, "sessionId", "id", default=None)
    connected = bool(pick(options, "connected", default=False))
    return {
        "provider": "deepseek",
        "sessionId": session_id,
        "connected": connected,
        "mode": pick(options, "mode", default="local"),
        "readOnly": bool(pick(options, "readOnly", default=True)),
        "status": "connected" if connected else "offline",
    }
