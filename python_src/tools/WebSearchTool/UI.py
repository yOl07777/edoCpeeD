"""Renderable WebSearchTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    return f"Search web for {data.get('query', '')}".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "web-search-use", "query": data.get("query", ""), "limit": data.get("limit")}


async def renderToolUseProgressMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "web-search-progress", "query": data.get("query", ""), "status": data.get("status", "searching")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    results = list(data.get("results") or [])
    return {
        "type": "web-search-result",
        "query": data.get("query", ""),
        "ok": bool(data.get("ok", True)),
        "results": results,
        "count": len(results),
        "error": data.get("error"),
        "suggestion": data.get("suggestion"),
    }


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseMessage",
    "renderToolUseProgressMessage",
]
