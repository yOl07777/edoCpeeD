from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def Stats(*args: Any, **kwargs: Any) -> Any:
    stats = option(args, kwargs, "stats", scalar_arg(args, first_options(args)))
    return component_payload("stats", stats=stats, keys=sorted(stats.keys()) if isinstance(stats, dict) else [])


__all__ = ["Stats"]
