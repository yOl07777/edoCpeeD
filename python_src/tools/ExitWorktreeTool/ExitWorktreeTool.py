"""Migrated local ExitWorktreeTool shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.worktree_store import exit_worktree


async def exit_worktree_tool() -> dict[str, Any]:
    return exit_worktree().to_dict()


ExitWorktreeTool = PythonTool(
    name="exit_worktree",
    description="Exit the local dry-run worktree context.",
    parameters=object_schema({}),
    handler=exit_worktree_tool,
    read_only=False,
)


__all__ = ["ExitWorktreeTool", "exit_worktree_tool"]
