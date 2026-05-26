from __future__ import annotations

from typing import Any

nodeCache: dict[str, Any] = {}
pendingClears: set[str] = set()
_absolute_removed = False


async def addPendingClear(*args: Any, **kwargs: Any) -> Any:
    key = str(args[0] if args else kwargs.get("key", "default"))
    pendingClears.add(key)
    return sorted(pendingClears)


async def consumeAbsoluteRemovedFlag(*args: Any, **kwargs: Any) -> Any:
    global _absolute_removed
    value = _absolute_removed
    _absolute_removed = False
    return value


def markAbsoluteRemoved() -> None:
    global _absolute_removed
    _absolute_removed = True
