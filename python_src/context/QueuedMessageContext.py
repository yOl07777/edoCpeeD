from __future__ import annotations

from collections import deque
from typing import Any


_QUEUE: deque[dict[str, Any]] = deque()


async def QueuedMessageProvider(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("clear"):
        _QUEUE.clear()
    messages = kwargs.get("messages", args[0] if args else None)
    if messages:
        for item in messages:
            _QUEUE.append(dict(item) if isinstance(item, dict) else {"text": str(item)})
    return await useQueuedMessage()


async def useQueuedMessage(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if "enqueue" in kwargs:
        item = kwargs["enqueue"]
        _QUEUE.append(dict(item) if isinstance(item, dict) else {"text": str(item)})
    item = _QUEUE.popleft() if kwargs.get("dequeue") and _QUEUE else None
    return {"provider": "deepseek", "queue": list(_QUEUE), "count": len(_QUEUE), "next": item}


__all__ = ["QueuedMessageProvider", "useQueuedMessage"]
