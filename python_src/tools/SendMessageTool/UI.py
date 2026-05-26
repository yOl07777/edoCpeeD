"""Renderable SendMessageTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = str(data.get("content", ""))
    return {"type": "send-message-use", "targetId": data.get("target_id") or data.get("targetId"), "sender": data.get("sender", "user"), "chars": len(content)}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "send-message-result", "id": data.get("id"), "sender": data.get("sender"), "content": data.get("content", "")}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
