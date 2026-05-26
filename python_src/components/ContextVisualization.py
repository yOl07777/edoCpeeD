from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, percent


async def ContextVisualization(*args: Any, **kwargs: Any) -> Any:
    used = option(args, kwargs, "used", option(args, kwargs, "tokens", 0))
    maximum = option(args, kwargs, "max", option(args, kwargs, "limit", option(args, kwargs, "total", 0)))
    usage_percent = percent(used, maximum)
    return component_payload("context_visualization", usedTokens=used, maxTokens=maximum, percent=usage_percent, nearLimit=usage_percent >= 80)


__all__ = ["ContextVisualization"]
