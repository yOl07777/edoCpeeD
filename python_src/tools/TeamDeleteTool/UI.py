"""Renderable TeamDeleteTool UI payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "team-delete-use", "teamId": data.get("team_id") or data.get("teamId")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "team-delete-result", "id": data.get("id"), "name": data.get("name"), "agentIds": data.get("agent_ids") or data.get("agentIds") or []}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
