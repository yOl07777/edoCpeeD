"""Prompt text and timeout defaults for BashTool."""

from __future__ import annotations

import os
from typing import Any


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


async def getDefaultTimeoutMs(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("timeoutMs") or kwargs.get("default") or _env_int("DEEPCODE_BASH_TIMEOUT_MS", 30_000))


async def getMaxTimeoutMs(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("maxTimeoutMs") or kwargs.get("maximum") or _env_int("DEEPCODE_BASH_MAX_TIMEOUT_MS", 600_000))


async def getSimplePrompt(*args: Any, **kwargs: Any) -> str:
    default_ms = await getDefaultTimeoutMs(**kwargs)
    max_ms = await getMaxTimeoutMs(**kwargs)
    return (
        "Run shell commands in the current workspace. Prefer read-only inspection commands when possible. "
        f"Default timeout is {default_ms} ms; maximum timeout is {max_ms} ms."
    )


__all__ = ["getDefaultTimeoutMs", "getMaxTimeoutMs", "getSimplePrompt"]
