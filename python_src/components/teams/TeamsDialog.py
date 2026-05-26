from __future__ import annotations

from typing import Any

from python_src.components.teams.TeamStatus import TeamStatus


async def TeamsDialog(*args: Any, **kwargs: Any) -> Any:
    members = kwargs.get("members") or (args[0] if args else []) or []
    return {"type": "teams_dialog", "provider": "deepseek", "status": await TeamStatus(members), "actions": ["open", "pause", "stop"]}


__all__ = ["TeamsDialog"]
