"""Renderable LSPTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    query = data.get("query") or data.get("symbol") or ""
    return f"Search symbols for {query}" if query else "Search symbols"


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "lsp-use",
        "query": data.get("query", ""),
        "path": data.get("path", "."),
        "include": data.get("include", "**/*"),
        "limit": data.get("limit"),
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    results = list(data.get("results") or [])
    return {
        "type": "lsp-result",
        "query": data.get("query", ""),
        "results": results,
        "count": data.get("count", len(results)),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "lsp-error", "query": data.get("query", ""), "error": data.get("error") or data.get("message", "")}


__all__ = [
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "userFacingName",
]
