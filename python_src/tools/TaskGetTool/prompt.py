"""Prompt text for TaskGetTool."""

from python_src.tools.TaskGetTool.constants import TASK_GET_TOOL_NAME

DESCRIPTION = "Get a local in-memory task by id."
PROMPT = f"Use {TASK_GET_TOOL_NAME} with an exact task_id returned by task_create or task_list."

__all__ = ["DESCRIPTION", "PROMPT"]
