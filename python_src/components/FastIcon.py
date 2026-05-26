from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def FastIcon(*args: Any, **kwargs: Any) -> Any:
    enabled = bool(option(args, kwargs, "enabled", scalar_arg(args, True)))
    return component_payload("fast_icon", enabled=enabled, icon=await getFastIconString(enabled=enabled))


async def getFastIconString(*args: Any, **kwargs: Any) -> Any:
    enabled = bool(option(args, kwargs, "enabled", scalar_arg(args, True)))
    return "FAST" if enabled else "SLOW"


__all__ = ["FastIcon", "getFastIconString"]
