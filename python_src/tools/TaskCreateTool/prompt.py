"""Prompt text for TaskCreateTool."""

from __future__ import annotations

from python_src.tools.TaskCreateTool.constants import TASK_CREATE_TOOL_NAME

DESCRIPTION = "Create an in-memory task for the current process."


async def getPrompt(*args, **kwargs) -> str:
    return f"Use {TASK_CREATE_TOOL_NAME} to create a local task record with title, optional description, and status."


__all__ = ["DESCRIPTION", "getPrompt"]
