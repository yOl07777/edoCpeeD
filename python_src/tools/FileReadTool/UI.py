"""Renderable FileReadTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _path(data: dict[str, Any]) -> str:
    return str(data.get("path") or data.get("file_path") or data.get("filePath") or "")


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    path = _path(data)
    return f"Read {path}" if path else "Read file"


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    path = _path(data)
    offset = data.get("offset")
    limit = data.get("limit")
    suffix = []
    if offset is not None:
        suffix.append(f"offset={offset}")
    if limit is not None:
        suffix.append(f"limit={limit}")
    detail = f" ({', '.join(suffix)})" if suffix else ""
    return f"Read {path}{detail}".strip()


async def renderToolUseTag(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-read-tag", "path": _path(data), "label": await userFacingName(data)}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "file-read-use",
        "tag": await renderToolUseTag(data),
        "offset": data.get("offset", 0),
        "limit": data.get("limit"),
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = str(data.get("content", ""))
    return {
        "type": "file-read-result",
        "path": _path(data),
        "lineCount": data.get("line_count") or data.get("lineCount"),
        "offset": data.get("offset", 0),
        "content": content,
        "bytes": len(content.encode("utf-8")),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-read-error", "path": _path(data), "error": data.get("error") or data.get("message", "")}


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseTag",
    "userFacingName",
]
