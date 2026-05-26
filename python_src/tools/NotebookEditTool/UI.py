"""Renderable NotebookEditTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def getToolUseSummary(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    return f"Edit notebook {data.get('path', '')} cell {data.get('cell_index', data.get('cellIndex', 0))}".strip()


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    source = str(data.get("source", ""))
    return {
        "type": "notebook-edit-use",
        "path": data.get("path", ""),
        "cellIndex": data.get("cell_index") or data.get("cellIndex", 0),
        "cellType": data.get("cell_type") or data.get("cellType"),
        "sourceLines": 0 if source == "" else source.count("\n") + 1,
    }


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {
        "type": "notebook-edit-result",
        "path": data.get("path", ""),
        "cellIndex": data.get("cell_index") or data.get("cellIndex"),
        "cellType": data.get("cell_type") or data.get("cellType"),
        "cellCount": data.get("cell_count") or data.get("cellCount"),
    }


async def renderToolUseErrorMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "notebook-edit-error", "path": data.get("path", ""), "error": data.get("error") or data.get("message", "")}


async def renderToolUseRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "notebook-edit-rejected", "path": data.get("path", ""), "reason": data.get("reason", "rejected")}


__all__ = [
    "getToolUseSummary",
    "renderToolResultMessage",
    "renderToolUseErrorMessage",
    "renderToolUseMessage",
    "renderToolUseRejectedMessage",
]
