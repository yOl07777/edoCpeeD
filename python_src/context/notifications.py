from __future__ import annotations

from collections import deque
from typing import Any


_NOTIFICATIONS: deque[dict[str, Any]] = deque()


async def getNext(*_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    return _NOTIFICATIONS.popleft() if _NOTIFICATIONS else None


async def useNotifications(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("clear"):
        _NOTIFICATIONS.clear()
    items = kwargs.get("items", args[0] if args else None)
    if items:
        for item in items:
            _NOTIFICATIONS.append(dict(item) if isinstance(item, dict) else {"text": str(item), "severity": "info"})
    if "push" in kwargs:
        item = kwargs["push"]
        _NOTIFICATIONS.append(dict(item) if isinstance(item, dict) else {"text": str(item), "severity": "info"})
    return {"provider": "deepseek", "notifications": list(_NOTIFICATIONS), "count": len(_NOTIFICATIONS), "getNext": getNext}


__all__ = ["getNext", "useNotifications"]
