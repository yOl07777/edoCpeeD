from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def HistorySearchDialog(*args: Any, **kwargs: Any) -> Any:
    query = str(option(args, kwargs, "query", ""))
    entries = normalize_items(option(args, kwargs, "entries", scalar_arg(args, [])))
    if query:
        entries = [entry for entry in entries if query.lower() in str(entry.get("text", "")).lower()]
    return component_payload("history_search_dialog", query=query, entries=entries, count=len(entries))


__all__ = ["HistorySearchDialog"]
