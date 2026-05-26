"""Renderable FileEditTool UI payload helpers."""

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
    return f"Edit {path}" if path else "Edit file"


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    count = data.get("replacements")
    suffix = f" ({count} replacements)" if count is not None else ""
    return f"Edit {_path(data)}{suffix}".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "file-edit-use",
        "path": _path(data),
        "oldText": data.get("old_text") or data.get("oldText", ""),
        "newText": data.get("new_text") or data.get("newText", ""),
        "replaceAll": bool(data.get("replace_all") or data.get("replaceAll", False)),
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "file-edit-result",
        "path": _path(data),
        "replacements": data.get("replacements", 0),
        "bytes": data.get("bytes"),
        "patch": data.get("patch"),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-edit-error", "path": _path(data), "error": data.get("error") or data.get("message", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "file-edit-rejected", "path": _path(data), "reason": data.get("reason", "rejected")}


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseRejectedMessage",
    "userFacingName",
]
