from __future__ import annotations


EXIT_REASONS = ["success", "error", "cancelled", "interrupted"]
HOOK_EVENTS = [
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "UserPromptSubmit",
    "SessionStart",
    "SessionEnd",
    "Stop",
]


__all__ = ["EXIT_REASONS", "HOOK_EVENTS"]
