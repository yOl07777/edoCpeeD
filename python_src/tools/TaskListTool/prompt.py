"""Prompt text for TaskListTool."""

from __future__ import annotations

from python_src.tools.TaskListTool.constants import TASK_LIST_TOOL_NAME

DESCRIPTION = "List local in-memory tasks for the current process."


async def getPrompt(*args, **kwargs) -> str:
    return f"Use {TASK_LIST_TOOL_NAME} to inspect local task records, optionally filtered by status."


__all__ = ["DESCRIPTION", "getPrompt"]
