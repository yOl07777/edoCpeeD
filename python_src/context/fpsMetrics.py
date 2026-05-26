from __future__ import annotations

import time
from typing import Any


_FPS_STATE: dict[str, Any] = {"frames": 0, "startedAt": time.perf_counter(), "lastFps": 0.0}


async def FpsMetricsProvider(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("reset"):
        _FPS_STATE.update({"frames": 0, "startedAt": time.perf_counter(), "lastFps": 0.0})
    if "frames" in kwargs:
        _FPS_STATE["frames"] = int(kwargs["frames"])
    return await useFpsMetrics()


async def useFpsMetrics(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    increment = int(kwargs.get("increment", 0) or 0)
    _FPS_STATE["frames"] += increment
    elapsed = max(time.perf_counter() - float(_FPS_STATE["startedAt"]), 0.001)
    _FPS_STATE["lastFps"] = round(float(_FPS_STATE["frames"]) / elapsed, 2)
    return {"provider": "deepseek", **_FPS_STATE, "elapsed": round(elapsed, 3)}


__all__ = ["FpsMetricsProvider", "useFpsMetrics"]
