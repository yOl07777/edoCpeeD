from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, percent, scalar_arg


async def MemoryUsageIndicator(*args: Any, **kwargs: Any) -> Any:
    used = option(args, kwargs, "used", option(args, kwargs, "usedBytes", scalar_arg(args, 0)))
    limit = option(args, kwargs, "limit", option(args, kwargs, "maxBytes", 0))
    usage = percent(used, limit)
    return component_payload("memory_usage_indicator", used=used, limit=limit, percent=usage, high=usage >= 80)


__all__ = ["MemoryUsageIndicator"]
