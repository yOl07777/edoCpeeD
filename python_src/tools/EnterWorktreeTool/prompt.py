"""Prompt helper for EnterWorktreeTool."""

from __future__ import annotations

from typing import Any


async def getEnterWorktreeToolPrompt(*args: Any, **kwargs: Any) -> str:
    return (
        "Use enter_worktree when work should be associated with a separate local worktree context. "
        "The Python migration records dry-run state only and does not create git worktrees."
    )


__all__ = ["getEnterWorktreeToolPrompt"]
