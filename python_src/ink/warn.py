from __future__ import annotations

from typing import Any


async def ifNotInteger(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value")
    name = str(args[1] if len(args) > 1 else kwargs.get("name", "value"))
    ok = isinstance(value, int) and not isinstance(value, bool)
    return None if ok else f"{name} must be an integer"
