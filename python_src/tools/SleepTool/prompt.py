"""Prompt constants for SleepTool."""

from __future__ import annotations

SLEEP_TOOL_NAME = "sleep"
DESCRIPTION = "Wait for a short duration, capped at 60 seconds."
SLEEP_TOOL_PROMPT = (
    "Use sleep only when a brief delay is necessary for polling or pacing. "
    "Do not use it for long waits; the Python shim enforces a 60 second cap."
)

__all__ = ["DESCRIPTION", "SLEEP_TOOL_NAME", "SLEEP_TOOL_PROMPT"]
