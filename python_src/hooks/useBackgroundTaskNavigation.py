from __future__ import annotations

from typing import Any


async def useBackgroundTaskNavigation(tasks: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    items = list(kwargs.get("tasks", tasks or []))
    index = int(kwargs.get("index", 0) or 0)
    key = str(kwargs.get("key", "")).lower()
    if key in {"j", "down", "arrowdown"}:
        index = min(len(items) - 1, index + 1) if items else 0
    elif key in {"k", "up", "arrowup"}:
        index = max(0, index - 1)
    selected = items[index] if items and 0 <= index < len(items) else None
    return {"provider": "deepseek", "tasks": items, "index": index, "selected": selected}


__all__ = ["useBackgroundTaskNavigation"]
