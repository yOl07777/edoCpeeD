"""Prompt constants for GlobTool."""

from __future__ import annotations

GLOB_TOOL_NAME = "glob_files"
DESCRIPTION = (
    "Find files by glob pattern inside the current workspace. Use a narrow path and pattern "
    "when possible, and use limit to keep results readable."
)

__all__ = ["DESCRIPTION", "GLOB_TOOL_NAME"]
