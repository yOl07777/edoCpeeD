"""Renderable TaskStopTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "task-stop-use", "taskId": data.get("task_id") or data.get("taskId"), "reason": data.get("reason", "")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "task-stop-result", "id": data.get("id"), "title": data.get("title"), "status": data.get("status"), "output": data.get("output", [])}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
