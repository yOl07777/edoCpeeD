from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def PrBadge(*args: Any, **kwargs: Any) -> Any:
    number = option(args, kwargs, "number", option(args, kwargs, "pr", scalar_arg(args, None)))
    state = str(option(args, kwargs, "state", "open"))
    return component_payload("pr_badge", number=number, state=state, text=f"PR #{number} {state}" if number is not None else f"PR {state}")


__all__ = ["PrBadge"]
