from __future__ import annotations

from typing import Any


async def useShowFastIconHint(*args: Any, **kwargs: Any) -> Any:
    return bool(kwargs.get("fastMode", args[0] if args else False))


__all__ = ["useShowFastIconHint"]
