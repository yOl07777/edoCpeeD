from __future__ import annotations

from typing import Any


async def useMergedTools(*tools: Any, **kwargs: Any) -> list[dict[str, Any]]:
    rows = list(kwargs.get("tools", tools or []))
    merged: dict[str, dict[str, Any]] = {}
    for group in rows:
        iterable = group if isinstance(group, (list, tuple)) else [group]
        for tool in iterable:
            if isinstance(tool, dict):
                name = tool.get("name") or (tool.get("function") or {}).get("name")
                merged[str(name)] = dict(tool)
            else:
                merged[str(tool)] = {"name": str(tool)}
    return list(merged.values())


__all__ = ["useMergedTools"]
