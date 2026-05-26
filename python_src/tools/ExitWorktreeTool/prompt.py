"""Prompt helper for ExitWorktreeTool."""

from __future__ import annotations

from typing import Any


async def getExitWorktreeToolPrompt(*args: Any, **kwargs: Any) -> str:
    return "Use exit_worktree when leaving a dry-run worktree context and returning to the main workspace context."


__all__ = ["getExitWorktreeToolPrompt"]
