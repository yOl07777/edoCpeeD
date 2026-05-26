"""Renderable FileWriteTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _path(data: dict[str, Any]) -> str:
    return str(data.get("path") or data.get("file_path") or data.get("filePath") or "")


def _content(data: dict[str, Any]) -> str:
    return str(data.get("content") or data.get("text") or "")


async def countLines(*args: Any, **kwargs: Any) -> int:
    value = str(args[0] if args else kwargs.get("content", ""))
    return 0 if value == "" else value.count("\n") + 1


async def isResultTruncated(*args: Any, **kwargs: Any) -> bool:
    data = _payload(args, kwargs)
    content = _content(data)
    limit = int(data.get("limit") or data.get("maxChars") or 20_000)
    return len(content) > limit or bool(data.get("truncated", False))


async def userFacingName(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    path = _path(data)
    return f"Write {path}" if path else "Write file"


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    lines = await countLines(_content(data))
    return f"Write {_path(data)} ({lines} lines)".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = _content(data)
    return {
        "type": "file-write-use",
        "path": _path(data),
        "lineCount": await countLines(content),
        "bytes": len(content.encode("utf-8")),
        "overwrite": data.get("overwrite", True),
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "file-write-result",
        "path": _path(data),
        "written": bool(data.get("written", True)),
        "bytes": data.get("bytes"),
        "truncated": await isResultTruncated(data),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-write-error", "path": _path(data), "error": data.get("error") or data.get("message", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-write-rejected", "path": _path(data), "reason": data.get("reason", "rejected")}


__all__ = [
    "countLines",
    "getToolUseSummary",
    "isResultTruncated",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseRejectedMessage",
    "userFacingName",
]
