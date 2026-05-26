from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, path_label, safe_int, scalar_arg


async def GlobalSearchDialog(*args: Any, **kwargs: Any) -> Any:
    query = str(option(args, kwargs, "query", ""))
    raw_results = option(args, kwargs, "results", scalar_arg(args, []))
    rows = [await parseRipgrepLine(item) if isinstance(item, str) else item for item in raw_results]
    if query:
        rows = [row for row in rows if query.lower() in str(row.get("text", "")).lower() or query.lower() in str(row.get("path", "")).lower()]
    return component_payload("global_search_dialog", query=query, results=rows, count=len(rows))


async def parseRipgrepLine(*args: Any, **kwargs: Any) -> Any:
    line = str(option(args, kwargs, "line", scalar_arg(args, "")))
    parts = line.split(":", 2)
    if len(parts) >= 3 and parts[1].isdigit():
        return {"path": path_label(parts[0]), "line": safe_int(parts[1]), "text": parts[2]}
    rows = normalize_items([line])
    return {"path": "", "line": None, "text": rows[0]["text"]}


__all__ = ["GlobalSearchDialog", "parseRipgrepLine"]
