"""Prompt text for TaskUpdateTool."""

from python_src.tools.TaskUpdateTool.constants import TASK_UPDATE_TOOL_NAME

DESCRIPTION = "Update title, description, or status on a local in-memory task."
PROMPT = f"Use {TASK_UPDATE_TOOL_NAME} with task_id and only the fields that should change."

__all__ = ["DESCRIPTION", "PROMPT"]
