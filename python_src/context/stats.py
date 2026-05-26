from __future__ import annotations

import time
from typing import Any


StatsContext: dict[str, Any] = {"counters": {}, "gauges": {}, "sets": {}, "timers": {}}


async def createStatsStore(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {"provider": "deepseek", **StatsContext}


async def StatsProvider(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("reset"):
        StatsContext["counters"].clear()
        StatsContext["gauges"].clear()
        StatsContext["sets"].clear()
        StatsContext["timers"].clear()
    return await useStats()


async def useCounter(name: Any = "default", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("name") or name or "default")
    amount = int(kwargs.get("amount", kwargs.get("increment", 1)) or 0)
    if kwargs.get("reset"):
        StatsContext["counters"][key] = 0
    else:
        StatsContext["counters"][key] = int(StatsContext["counters"].get(key, 0)) + amount
    return {"name": key, "value": StatsContext["counters"][key]}


async def useGauge(name: Any = "default", value: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("name") or name or "default")
    gauge_value = kwargs.get("value", value if value is not None else 0)
    StatsContext["gauges"][key] = float(gauge_value)
    return {"name": key, "value": StatsContext["gauges"][key]}


async def useSet(name: Any = "default", value: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("name") or name or "default")
    bucket = StatsContext["sets"].setdefault(key, set())
    if value is not None:
        bucket.add(value)
    for item in kwargs.get("values", []) or []:
        bucket.add(item)
    return {"name": key, "values": sorted(str(item) for item in bucket), "count": len(bucket)}


async def useTimer(name: Any = "default", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("name") or name or "default")
    started = float(kwargs.get("startedAt", time.perf_counter()))
    elapsed = max(time.perf_counter() - started, 0.0)
    StatsContext["timers"][key] = elapsed
    return {"name": key, "elapsed": elapsed}


async def useStats(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "counters": dict(StatsContext["counters"]),
        "gauges": dict(StatsContext["gauges"]),
        "sets": {key: sorted(str(item) for item in value) for key, value in StatsContext["sets"].items()},
        "timers": dict(StatsContext["timers"]),
    }


__all__ = ["StatsContext", "StatsProvider", "createStatsStore", "useCounter", "useGauge", "useSet", "useStats", "useTimer"]
