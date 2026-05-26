"""Analytics sink kill switch."""

from __future__ import annotations

import os
from typing import Any


async def isSinkKilled(config: dict[str, Any] | None = None) -> bool:
    config = config or {}
    if "sinkKilled" in config:
        return bool(config["sinkKilled"])
    value = os.getenv("DEEPSEEK_ANALYTICS_SINK_KILLED") or os.getenv("ANALYTICS_SINK_KILLED")
    return str(value).lower() in {"1", "true", "yes", "on"} if value is not None else False
