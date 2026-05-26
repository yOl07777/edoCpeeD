"""Configuration for time-based microcompact."""

from __future__ import annotations

import os
from typing import Any


TIME_BASED_MC_CONFIG_DEFAULTS = {
    "enabled": False,
    "gapThresholdMinutes": 60,
    "keepRecent": 5,
}


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


async def getTimeBasedMCConfig(*_: Any, **__: Any) -> dict[str, Any]:
    return {
        "enabled": _bool_env("DEEPSEEK_TIME_BASED_MICROCOMPACT", TIME_BASED_MC_CONFIG_DEFAULTS["enabled"]),
        "gapThresholdMinutes": _int_env(
            "DEEPSEEK_TIME_BASED_MC_GAP_MINUTES",
            TIME_BASED_MC_CONFIG_DEFAULTS["gapThresholdMinutes"],
        ),
        "keepRecent": _int_env("DEEPSEEK_TIME_BASED_MC_KEEP_RECENT", TIME_BASED_MC_CONFIG_DEFAULTS["keepRecent"]),
    }


__all__ = ["TIME_BASED_MC_CONFIG_DEFAULTS", "getTimeBasedMCConfig"]
