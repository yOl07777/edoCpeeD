from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, safe_float, scalar_arg


async def CostThresholdDialog(*args: Any, **kwargs: Any) -> Any:
    current = safe_float(option(args, kwargs, "current", option(args, kwargs, "cost", scalar_arg(args, 0))))
    threshold = safe_float(option(args, kwargs, "threshold", option(args, kwargs, "limit", 0)))
    return component_payload("cost_threshold_dialog", current=current, threshold=threshold, exceeded=threshold > 0 and current >= threshold)


__all__ = ["CostThresholdDialog"]
