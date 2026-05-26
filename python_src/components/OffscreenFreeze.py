from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def OffscreenFreeze(*args: Any, **kwargs: Any) -> Any:
    frozen = bool(option(args, kwargs, "frozen", scalar_arg(args, True)))
    return component_payload("offscreen_freeze", frozen=frozen, reason=str(option(args, kwargs, "reason", "offscreen")))


__all__ = ["OffscreenFreeze"]
