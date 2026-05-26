"""API context-management config shim."""

from __future__ import annotations

import os
from typing import Any


DEFAULT_MAX_INPUT_TOKENS = 180_000
DEFAULT_TARGET_INPUT_TOKENS = 40_000
TOOLS_CLEARABLE_RESULTS = ["Bash", "run_shell", "PowerShell", "Glob", "Grep", "Read", "WebFetch", "WebSearch"]
TOOLS_CLEARABLE_USES = ["Edit", "Write", "NotebookEdit"]


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


async def getAPIContextManagement(options: dict[str, Any] | None = None, *_: Any, **__: Any) -> dict[str, Any] | None:
    opts = options or {}
    strategies: list[dict[str, Any]] = []
    has_thinking = bool(opts.get("hasThinking", False))
    redact_thinking = bool(opts.get("isRedactThinkingActive", False))
    clear_all_thinking = bool(opts.get("clearAllThinking", False))

    if has_thinking and not redact_thinking:
        strategies.append(
            {
                "type": "clear_thinking_20251015",
                "keep": {"type": "thinking_turns", "value": 1} if clear_all_thinking else "all",
            }
        )

    if os.getenv("USER_TYPE") == "ant":
        trigger_threshold = _int_env("API_MAX_INPUT_TOKENS", DEFAULT_MAX_INPUT_TOKENS)
        keep_target = _int_env("API_TARGET_INPUT_TOKENS", DEFAULT_TARGET_INPUT_TOKENS)
        clear_at_least = max(1, trigger_threshold - keep_target)
        if _truthy(os.getenv("USE_API_CLEAR_TOOL_RESULTS")):
            strategies.append(
                {
                    "type": "clear_tool_uses_20250919",
                    "trigger": {"type": "input_tokens", "value": trigger_threshold},
                    "clear_at_least": {"type": "input_tokens", "value": clear_at_least},
                    "clear_tool_inputs": TOOLS_CLEARABLE_RESULTS,
                }
            )
        if _truthy(os.getenv("USE_API_CLEAR_TOOL_USES")):
            strategies.append(
                {
                    "type": "clear_tool_uses_20250919",
                    "trigger": {"type": "input_tokens", "value": trigger_threshold},
                    "clear_at_least": {"type": "input_tokens", "value": clear_at_least},
                    "exclude_tools": TOOLS_CLEARABLE_USES,
                }
            )

    return {"edits": strategies} if strategies else None


__all__ = [
    "DEFAULT_MAX_INPUT_TOKENS",
    "DEFAULT_TARGET_INPUT_TOKENS",
    "TOOLS_CLEARABLE_RESULTS",
    "TOOLS_CLEARABLE_USES",
    "getAPIContextManagement",
]
