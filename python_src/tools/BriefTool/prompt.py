"""
Python migration draft for `src/tools/BriefTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

BRIEF_TOOL_NAME = "brief"
LEGACY_BRIEF_TOOL_NAME = "task_brief"
DESCRIPTION = "Create a local structured brief with optional workspace attachments."
BRIEF_PROACTIVE_SECTION = "Use brief when the user wants a concise handoff summary with attached local files."
BRIEF_TOOL_PROMPT = (
    "Prepare a concise brief. Include title, body, and any workspace-relative attachment paths. "
    "This Python migration stores metadata locally and does not upload files."
)

__all__ = [
    "BRIEF_PROACTIVE_SECTION",
    "BRIEF_TOOL_NAME",
    "BRIEF_TOOL_PROMPT",
    "DESCRIPTION",
    "LEGACY_BRIEF_TOOL_NAME",
]
