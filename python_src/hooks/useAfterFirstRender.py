from __future__ import annotations

from typing import Any


_RENDERED = False


async def useAfterFirstRender(*_args: Any, **kwargs: Any) -> bool:
    global _RENDERED
    if kwargs.get("reset"):
        _RENDERED = False
        return False
    was_after = _RENDERED
    _RENDERED = True
    return was_after


__all__ = ["useAfterFirstRender"]
