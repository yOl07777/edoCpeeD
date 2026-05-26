from __future__ import annotations

from typing import Any


async def mergeClients(*clients: Any, **kwargs: Any) -> list[dict[str, Any]]:
    rows = list(kwargs.get("clients", clients or []))
    merged: dict[str, dict[str, Any]] = {}
    for client in rows:
        if isinstance(client, (list, tuple)):
            for item in client:
                key = str(item.get("id") or item.get("name"))
                merged[key] = dict(item)
        elif isinstance(client, dict):
            key = str(client.get("id") or client.get("name"))
            merged[key] = dict(client)
    return list(merged.values())


async def useMergedClients(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return await mergeClients(*args, **kwargs)


__all__ = ["mergeClients", "useMergedClients"]
