"""Migrated local EnterWorktreeTool shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.worktree_store import enter_worktree


async def enter_worktree_tool(
    path: str | None = None,
    *,
    branch: str = "",
    reason: str = "",
    cwd: str | None = None,
) -> dict[str, Any]:
    return enter_worktree(path, branch=branch, reason=reason, cwd=cwd).to_dict()


EnterWorktreeTool = PythonTool(
    name="enter_worktree",
    description="Record entry into a local dry-run worktree context.",
    parameters=object_schema(
        {
            "path": {"type": "string"},
            "branch": {"type": "string"},
            "reason": {"type": "string"},
        }
    ),
    handler=enter_worktree_tool,
    read_only=False,
)


__all__ = ["EnterWorktreeTool", "enter_worktree_tool"]
