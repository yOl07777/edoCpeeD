from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useSSHSession(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    host = str(pick(options, "host", default=""))
    user = str(pick(options, "user", "username", default=""))
    connected = bool(pick(options, "connected", default=False))
    return {
        "provider": "deepseek",
        "host": host,
        "user": user,
        "connected": connected,
        "target": f"{user + '@' if user else ''}{host}" if host else "",
        "status": "connected" if connected else "not_connected",
    }
