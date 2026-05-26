"""Prompt constants for RemoteTriggerTool."""

from __future__ import annotations

REMOTE_TRIGGER_TOOL_NAME = "remote_trigger"
DESCRIPTION = "Record a lightweight remote trigger event in local schedule state."
PROMPT = (
    "Use this shim to record that an external trigger would be fired. "
    "It does not call remote services or wake external workers."
)

__all__ = ["DESCRIPTION", "PROMPT", "REMOTE_TRIGGER_TOOL_NAME"]
