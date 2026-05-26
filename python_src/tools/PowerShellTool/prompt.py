"""Prompt text and timeout defaults for PowerShellTool."""

from __future__ import annotations

import os
from typing import Any

from python_src.tools.PowerShellTool.toolName import POWERSHELL_TOOL_NAME


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


async def getDefaultTimeoutMs(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("timeoutMs") or kwargs.get("default") or _env_int("DEEPCODE_POWERSHELL_TIMEOUT_MS", 30_000))


async def getMaxTimeoutMs(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("maxTimeoutMs") or kwargs.get("maximum") or _env_int("DEEPCODE_POWERSHELL_MAX_TIMEOUT_MS", 600_000))


async def getPrompt(*args: Any, **kwargs: Any) -> str:
    default_ms = await getDefaultTimeoutMs(**kwargs)
    max_ms = await getMaxTimeoutMs(**kwargs)
    return (
        "Run PowerShell commands in the current workspace. Prefer read-only inspection commands, "
        "avoid destructive file or git operations unless explicitly requested, and keep output focused. "
        f"Tool name: {kwargs.get('toolName') or POWERSHELL_TOOL_NAME}. "
        f"Default timeout is {default_ms} ms; maximum timeout is {max_ms} ms."
    )


__all__ = ["getDefaultTimeoutMs", "getMaxTimeoutMs", "getPrompt"]
