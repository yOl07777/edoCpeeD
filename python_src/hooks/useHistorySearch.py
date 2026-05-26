from __future__ import annotations

from typing import Any


async def useHistorySearch(history: list[Any] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    items = [str(item) for item in kwargs.get("history", history or [])]
    query = str(kwargs.get("query", "") or "").lower()
    matches = [item for item in items if query in item.lower()] if query else items
    index = max(0, min(int(kwargs.get("index", 0) or 0), max(len(matches) - 1, 0)))
    return {"provider": "deepseek", "query": query, "results": matches, "selected": matches[index] if matches else "", "index": index}


__all__ = ["useHistorySearch"]
