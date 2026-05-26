"""Analytics sink bootstrap helpers."""

from __future__ import annotations

from typing import Any

from .growthbook import initializeGrowthBook
from .index import attachAnalyticsSink
from .sinkKillswitch import isSinkKilled


async def initializeAnalyticsGates(features: dict[str, Any] | None = None) -> dict[str, Any]:
    return await initializeGrowthBook(features)


async def initializeAnalyticsSink(sink: Any | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    if await isSinkKilled(config):
        return {"attached": False, "killed": True}
    if sink is None:
        return {"attached": False, "killed": False}
    handle = await attachAnalyticsSink(sink)
    return {"attached": True, "killed": False, **handle}
