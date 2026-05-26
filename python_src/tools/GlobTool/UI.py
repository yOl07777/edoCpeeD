"""Renderable GlobTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    pattern = data.get("pattern") or "*"
    return f"Find files matching {pattern}"


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    pattern = data.get("pattern") or "*"
    root = data.get("path") or data.get("root") or "."
    limit = data.get("limit")
    suffix = f", limit={limit}" if limit is not None else ""
    return f"Glob {pattern} in {root}{suffix}"


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "glob-use",
        "pattern": data.get("pattern", "*"),
        "path": data.get("path", "."),
        "limit": data.get("limit"),
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    matches = list(data.get("matches") or [])
    return {
        "type": "glob-result",
        "root": data.get("root") or data.get("path") or ".",
        "pattern": data.get("pattern", "*"),
        "matches": matches,
        "count": len(matches),
        "truncated": bool(data.get("truncated", False)),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "glob-error", "pattern": data.get("pattern", "*"), "error": data.get("error") or data.get("message", "")}


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "userFacingName",
]
