"""Renderable ExitWorktreeTool payload helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {**(args[0] if args and isinstance(args[0], dict) else {}), **kwargs}


async def renderToolUseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "exit-worktree-use"}


async def renderToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return {"type": "exit-worktree-result", "active": data.get("active", False), "path": data.get("path", "")}


__all__ = ["renderToolResultMessage", "renderToolUseMessage"]
