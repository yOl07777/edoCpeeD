"""FileEditTool constants."""

from __future__ import annotations

FILE_EDIT_TOOL_NAME = "edit_file"
FILE_UNEXPECTEDLY_MODIFIED_ERROR = "File was unexpectedly modified before edit could be applied."
CLAUDE_FOLDER_PERMISSION_PATTERN = ".claude/**"
GLOBAL_CLAUDE_FOLDER_PERMISSION_PATTERN = "~/.claude/**"

__all__ = [
    "CLAUDE_FOLDER_PERMISSION_PATTERN",
    "FILE_EDIT_TOOL_NAME",
    "FILE_UNEXPECTEDLY_MODIFIED_ERROR",
    "GLOBAL_CLAUDE_FOLDER_PERMISSION_PATTERN",
]
