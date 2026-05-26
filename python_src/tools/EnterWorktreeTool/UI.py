"""Renderable EnterWorktreeTool payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "enter-worktree-use", "path": data.get("path"), "branch": data.get("branch", "")}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "enter-worktree-result", "active": data.get("active", True), "path": data.get("path"), "branch": data.get("branch", "")}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
