"""Prompt text for TodoWriteTool."""

from python_src.tools.TodoWriteTool.constants import TODO_WRITE_TOOL_NAME

DESCRIPTION = "Create or replace the local todo list for the current task."
PROMPT = f"Use {TODO_WRITE_TOOL_NAME} with a complete todo list; valid statuses are pending, in_progress, and completed."

__all__ = ["DESCRIPTION", "PROMPT"]
