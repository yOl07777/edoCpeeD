from __future__ import annotations

from typing import Any

async def useAnimationFrame(*args: Any, **kwargs: Any) -> Any:
    callback = args[0] if args else kwargs.get("callback")
    enabled = bool(kwargs.get("enabled", True))
    frame = int(kwargs.get("frame", 0))
    if enabled and callable(callback):
        callback(frame)
    return {"provider": "deepseek", "enabled": enabled, "frame": frame, "scheduled": enabled}
