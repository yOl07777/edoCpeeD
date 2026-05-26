from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg
from python_src.components.EffortIndicator import effortLevelToSymbol, getEffortNotificationText


async def EffortCallout(*args: Any, **kwargs: Any) -> Any:
    level = str(option(args, kwargs, "level", scalar_arg(args, "medium")))
    return component_payload(
        "effort_callout",
        level=level,
        visible=await shouldShowEffortCallout(*args, **kwargs),
        symbol=await effortLevelToSymbol(level),
        text=await getEffortNotificationText(level),
    )


async def shouldShowEffortCallout(*args: Any, **kwargs: Any) -> Any:
    if bool(option(args, kwargs, "dismissed", False)):
        return False
    level = str(option(args, kwargs, "level", scalar_arg(args, "medium"))).lower()
    return bool(option(args, kwargs, "enabled", True)) and level in {"high", "xhigh", "extra", "max"}


__all__ = ["EffortCallout", "shouldShowEffortCallout"]
