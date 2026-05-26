"""Renderable RemoteTriggerTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "remote-trigger-use", "name": data.get("name", ""), "payload": data.get("payload", {})}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "remote-trigger-result",
        "id": data.get("id"),
        "name": data.get("name", ""),
        "payload": data.get("payload", {}),
        "createdAt": data.get("created_at") or data.get("createdAt"),
    }


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
