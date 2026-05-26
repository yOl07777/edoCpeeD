"""Renderable ConfigTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "config-use", "action": data.get("action", "get"), "key": data.get("key")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "config-result",
        "key": data.get("key"),
        "value": data.get("value"),
        "path": data.get("path"),
        "removed": data.get("removed"),
        "config": data.get("config"),
    }


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "config-rejected", "key": data.get("key"), "reason": data.get("reason", "rejected")}


__all__ = ["renderToolResultMessage", "renderToolUseMessage", "renderToolUseRejectedMessage"]
