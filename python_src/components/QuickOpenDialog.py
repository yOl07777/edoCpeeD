from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def QuickOpenDialog(*args: Any, **kwargs: Any) -> Any:
    query = str(option(args, kwargs, "query", ""))
    items = normalize_items(option(args, kwargs, "items", scalar_arg(args, [])))
    if query:
        items = [item for item in items if query.lower() in str(item.get("text", item.get("path", ""))).lower()]
    return component_payload("quick_open_dialog", query=query, items=items, count=len(items))


__all__ = ["QuickOpenDialog"]
