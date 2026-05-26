from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def InterruptedByUser(*args: Any, **kwargs: Any) -> Any:
    reason = str(option(args, kwargs, "reason", scalar_arg(args, "Interrupted by user")))
    return component_payload("interrupted_by_user", interrupted=True, reason=reason)


__all__ = ["InterruptedByUser"]
