"""Renderable ReadMcpResourceTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    return f"Read MCP resource {data.get('uri', '')}".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "read-mcp-resource-use", "uri": data.get("uri", "")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = str(data.get("content", ""))
    return {
        "type": "read-mcp-resource-result",
        "uri": data.get("uri", ""),
        "name": data.get("name"),
        "mimeType": data.get("mime_type") or data.get("mimeType"),
        "server": data.get("server"),
        "content": content,
        "chars": len(content),
    }


__all__ = ["renderToolResultMessage", "renderToolUseMessage", "userFacingName"]
