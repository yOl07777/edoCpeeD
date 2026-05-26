"""Renderable WebFetchTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    return f"Fetch {data.get('url', '')}".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "web-fetch-use", "url": data.get("url", ""), "maxChars": data.get("max_chars") or data.get("maxChars")}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "web-fetch-progress", "url": data.get("url", ""), "status": data.get("status", "fetching")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = str(data.get("content", ""))
    return {
        "type": "web-fetch-result",
        "url": data.get("url", ""),
        "ok": bool(data.get("ok", True)),
        "statusCode": data.get("status_code") or data.get("statusCode"),
        "contentType": data.get("content_type") or data.get("contentType"),
        "content": content,
        "chars": len(content),
        "truncated": bool(data.get("truncated", False)),
        "error": data.get("error"),
        "suggestion": data.get("suggestion"),
    }


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
]
