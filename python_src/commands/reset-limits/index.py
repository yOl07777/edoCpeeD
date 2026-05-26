from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def _state_paths(cwd: str | None = None) -> list[str]:
    root = Path(cwd or Path.cwd())
    return [
        str(root / ".deepseek" / "mock-rate-limits.json"),
        str(root / ".deepseek" / "rate-limit-state.json"),
    ]


async def resetLimitsNonInteractive(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    cwd = kwargs.get("cwd")
    return {
        "type": "reset_limits",
        "provider": "deepseek",
        "dryRun": bool(kwargs.get("dryRun", True)),
        "paths": _state_paths(cwd),
        "message": "Local DeepSeek mock/rate-limit state can be reset by removing these files.",
    }


async def resetLimits(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    result = await resetLimitsNonInteractive(cwd=cwd, args=args)
    value = result["message"]
    if onDone:
        onDone(value)
    result["value"] = value
    return result


reset_limits = {
    "type": "local",
    "name": "reset-limits",
    "description": "Show how to reset local DeepSeek rate-limit mock state",
    "supportsNonInteractive": True,
    "source": "builtin",
    "call": resetLimits,
}

default = reset_limits


__all__ = ["default", "resetLimits", "resetLimitsNonInteractive", "reset_limits"]
