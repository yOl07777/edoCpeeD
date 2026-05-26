"""REPLTool constants and feature flag."""

from __future__ import annotations

import os
from typing import Any

REPL_TOOL_NAME = "repl"
REPL_ONLY_TOOLS = {"synthetic_output", "testing_permission"}


async def isReplModeEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    return os.getenv("DEEPCODE_REPL_MODE", "").lower() in {"1", "true", "yes", "on"}


__all__ = ["REPL_ONLY_TOOLS", "REPL_TOOL_NAME", "isReplModeEnabled"]
