"""Renderable ScheduleCronTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderCreateToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "cron-create-use", "name": data.get("name", ""), "schedule": data.get("schedule", ""), "prompt": data.get("prompt", "")}


async def renderCreateResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "cron-create-result", "id": data.get("id"), "name": data.get("name", ""), "schedule": data.get("schedule", ""), "status": data.get("status")}


async def renderListToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "cron-list-use", "status": data.get("status")}


async def renderListResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    crons = list(data.get("crons") or [])
    return {"type": "cron-list-result", "count": data.get("count", len(crons)), "crons": crons}


async def renderDeleteToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "cron-delete-use", "cronId": data.get("cron_id") or data.get("cronId")}


async def renderDeleteResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "cron-delete-result", "id": data.get("id"), "name": data.get("name", ""), "status": data.get("status", "deleted")}


__all__ = [
    "renderCreateResultMessage",
    "renderCreateToolUseMessage",
    "renderDeleteResultMessage",
    "renderDeleteToolUseMessage",
    "renderListResultMessage",
    "renderListToolUseMessage",
]
