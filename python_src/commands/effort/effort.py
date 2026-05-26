"""Implementation for `/effort`."""

from __future__ import annotations

import os
from typing import Any, Callable

EFFORT_LEVELS = ("low", "medium", "high", "max")
EFFORT_DESCRIPTIONS = {
    "low": "Quick, straightforward implementation",
    "medium": "Balanced approach with standard testing",
    "high": "Comprehensive implementation with extensive testing",
    "max": "Maximum capability with deepest reasoning",
}
_state: dict[str, str | None] = {"effort": None}


def _env_override() -> str | None:
    value = os.getenv("DEEPSEEK_CODE_EFFORT_LEVEL") or os.getenv("CLAUDE_CODE_EFFORT_LEVEL")
    return value.lower() if value else None


def showCurrentEffort(appStateEffort: str | None = None, model: str = "deepseek-chat") -> dict[str, Any]:
    env = _env_override()
    effective = env if env not in {None, "auto", "unset"} else (appStateEffort or _state.get("effort"))
    if effective is None:
        return {"message": f"Effort level: auto for {model}", "value": None}
    return {"message": f"Current effort level: {effective} ({EFFORT_DESCRIPTIONS.get(effective, 'custom')})", "value": effective}


def executeEffort(args: str) -> dict[str, Any]:
    normalized = (args or "").strip().lower()
    if normalized in {"auto", "unset"}:
        _state["effort"] = None
        return {"message": "Effort level set to auto", "effortUpdate": {"value": None}}
    if normalized not in EFFORT_LEVELS:
        return {"message": f"Invalid argument: {args}. Valid options are: low, medium, high, max, auto", "error": True}
    _state["effort"] = normalized
    return {
        "message": f"Set effort level to {normalized}: {EFFORT_DESCRIPTIONS[normalized]}",
        "effortUpdate": {"value": normalized},
    }


async def call(onDone: Callable[..., Any] | None = None, _context: Any = None, args: str | None = "") -> dict[str, Any]:
    arg = (args or "").strip()
    if arg in {"help", "-h", "--help"}:
        message = "Usage: /effort [low|medium|high|max|auto]"
        result = {"message": message}
    elif not arg or arg in {"current", "status"}:
        result = showCurrentEffort()
    else:
        result = executeEffort(arg)
    if onDone:
        onDone(result["message"])
    return result
