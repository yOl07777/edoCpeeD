from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick, text_filter


async def useSearchInput(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    query = str(pick(options, "query", "value", default=""))
    items = listify(pick(options, "items", default=[]))
    key = pick(options, "key", default=None)
    results = text_filter(items, query, key=key)
    return {"provider": "deepseek", "query": query, "results": results, "count": len(results)}
