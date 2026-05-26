from __future__ import annotations

from typing import Any


async def useMergedCommands(*commands: Any, **kwargs: Any) -> list[dict[str, Any]]:
    rows = list(kwargs.get("commands", commands or []))
    merged: dict[str, dict[str, Any]] = {}
    for group in rows:
        iterable = group if isinstance(group, (list, tuple)) else [group]
        for command in iterable:
            if isinstance(command, dict):
                merged[str(command.get("name"))] = dict(command)
            else:
                merged[str(command)] = {"name": str(command)}
    return list(merged.values())


__all__ = ["useMergedCommands"]
