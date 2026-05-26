from __future__ import annotations

from typing import Any


async def useArrowKeyHistory(history: list[str] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    items = list(kwargs.get("history", history or []))
    index = int(kwargs.get("index", len(items)) or 0)
    key = str(kwargs.get("key", "")).lower()
    if key in {"up", "arrowup"}:
        index = max(0, index - 1)
    elif key in {"down", "arrowdown"}:
        index = min(len(items), index + 1)
    value = items[index] if 0 <= index < len(items) else ""
    return {"provider": "deepseek", "history": items, "index": index, "value": value}


__all__ = ["useArrowKeyHistory"]
