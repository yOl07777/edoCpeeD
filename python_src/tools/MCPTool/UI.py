"""Renderable MCPTool UI payload helpers."""

from __future__ import annotations

import json
from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def tryUnwrapTextPayload(*args: Any, **kwargs: Any) -> str | None:
    value = args[0] if args else kwargs.get("payload")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        content = value.get("content")
        if isinstance(content, list):
            texts = [item.get("text") for item in content if isinstance(item, dict) and isinstance(item.get("text"), str)]
            return "\n".join(texts) if texts else None
    return None


async def tryFlattenJson(*args: Any, **kwargs: Any) -> dict[str, Any] | list[Any] | str:
    value = args[0] if args else kwargs.get("payload")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, dict) and set(value) == {"content"} and isinstance(value["content"], list):
        return value["content"]
    return value


async def trySlackSendCompact(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    data = _payload(args, kwargs)
    tool = str(data.get("tool") or data.get("name") or "").lower()
    arguments = data.get("arguments") if isinstance(data.get("arguments"), dict) else data
    if "slack" not in tool or "send" not in tool:
        return None
    return {
        "channel": arguments.get("channel") or arguments.get("channel_id"),
        "text": arguments.get("text") or arguments.get("message", ""),
    }


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "mcp-use", "server": data.get("server"), "tool": data.get("tool") or data.get("name"), "arguments": data.get("arguments", {})}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "mcp-progress", "server": data.get("server"), "tool": data.get("tool") or data.get("name"), "status": data.get("status", "running")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    unwrapped = await tryUnwrapTextPayload(data.get("result", data))
    flattened = await tryFlattenJson(unwrapped if unwrapped is not None else data.get("result", data))
    return {
        "type": "mcp-result",
        "server": data.get("server"),
        "tool": data.get("tool") or data.get("name"),
        "ok": bool(data.get("ok", True)),
        "result": flattened,
        "text": unwrapped,
    }


__all__ = [
    "renderToolResultMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
    "tryFlattenJson",
    "trySlackSendCompact",
    "tryUnwrapTextPayload",
]
