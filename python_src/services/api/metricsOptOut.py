"""Metrics opt-out helper."""

from __future__ import annotations

import os
from typing import Any

_CACHE: bool | None = None


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


async def _clearMetricsEnabledCacheForTesting() -> None:
    global _CACHE
    _CACHE = None


async def checkMetricsEnabled(config: dict[str, Any] | None = None) -> bool:
    """Return false when metrics are disabled by env/config."""

    global _CACHE
    if config:
        for key in ("metricsEnabled", "telemetryEnabled"):
            if key in config:
                return bool(config[key])
        for key in ("metricsDisabled", "telemetryDisabled"):
            if key in config:
                return not bool(config[key])
    if _CACHE is not None:
        return _CACHE
    disabled = any(
        _truthy(os.getenv(name))
        for name in (
            "DEEPSEEK_DISABLE_METRICS",
            "DEEPSEEK_DISABLE_ANALYTICS",
            "DISABLE_METRICS",
            "DO_NOT_TRACK",
        )
    )
    _CACHE = not disabled
    return _CACHE

