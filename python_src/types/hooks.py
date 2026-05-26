from __future__ import annotations

from typing import Any

HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "UserPromptSubmit",
    "SessionStart",
    "Setup",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "Notification",
    "PermissionRequest",
    "PermissionDenied",
    "Elicitation",
    "ElicitationResult",
    "CwdChanged",
    "FileChanged",
    "WorktreeCreate",
    "TaskCompleted",
    "TeammateIdle",
}

promptRequestSchema = {
    "type": "object",
    "required": ["prompt", "message", "options"],
    "properties": {
        "prompt": {"type": "string"},
        "message": {"type": "string"},
        "options": {"type": "array"},
    },
}
syncHookResponseSchema = {"type": "object"}
hookJSONOutputSchema = {"oneOf": [{"required": ["async"]}, syncHookResponseSchema]}


def isHookEvent(value: str) -> bool:
    return value in HOOK_EVENTS


def isSyncHookJSONOutput(json_value: dict[str, Any]) -> bool:
    return not (isinstance(json_value, dict) and json_value.get("async") is True)


def isAsyncHookJSONOutput(json_value: dict[str, Any]) -> bool:
    return isinstance(json_value, dict) and json_value.get("async") is True


__all__ = [
    "HOOK_EVENTS",
    "hookJSONOutputSchema",
    "isAsyncHookJSONOutput",
    "isHookEvent",
    "isSyncHookJSONOutput",
    "promptRequestSchema",
    "syncHookResponseSchema",
]
