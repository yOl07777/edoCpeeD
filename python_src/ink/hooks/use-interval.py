from __future__ import annotations

from typing import Any

async def useAnimationTimer(*args: Any, **kwargs: Any) -> Any:
    interval = int(kwargs.get("interval", kwargs.get("delay", 16)))
    running = bool(kwargs.get("running", kwargs.get("enabled", True)))
    return {"provider": "deepseek", "interval": interval, "running": running, "nextFrameMs": interval if running else None}

async def useInterval(*args: Any, **kwargs: Any) -> Any:
    callback = args[0] if args else kwargs.get("callback")
    delay = kwargs.get("delay", args[1] if len(args) > 1 else None)
    enabled = delay is not None and bool(kwargs.get("enabled", True))
    ticks = int(kwargs.get("ticks", 0))
    if enabled and callable(callback):
        callback()
        ticks += 1
    return {"provider": "deepseek", "enabled": enabled, "delay": delay, "ticks": ticks}
