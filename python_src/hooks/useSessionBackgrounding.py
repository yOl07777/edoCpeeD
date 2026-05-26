from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useSessionBackgrounding(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    backgrounded = bool(pick(options, "backgrounded", "enabled", default=False))
    return {
        "provider": "deepseek",
        "backgrounded": backgrounded,
        "sessionId": pick(options, "sessionId", default=None),
        "message": "Session is running in the background." if backgrounded else "Session remains in the foreground.",
    }
