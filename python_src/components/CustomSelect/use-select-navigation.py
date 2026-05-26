from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import clamp_index, select_payload


async def useSelectNavigation(*args: Any, **kwargs: Any) -> Any:
    index = int(kwargs.get("index") or (args[0] if args else 0) or 0)
    count = int(kwargs.get("count") or (args[1] if len(args) > 1 else 0) or 0)
    delta = int(kwargs.get("delta") or 0)
    next_index = clamp_index(index + delta, count)
    return select_payload("select_navigation", index=index, nextIndex=next_index, count=count)


__all__ = ["useSelectNavigation"]
