"""Renderable ListMcpResourcesTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "list-mcp-resources-use", "server": data.get("server")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    resources = list(data.get("resources") or [])
    return {"type": "list-mcp-resources-result", "count": data.get("count", len(resources)), "resources": resources}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
