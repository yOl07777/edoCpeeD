"""Analytics opt-out configuration for the Python runtime."""

from __future__ import annotations

import os
from typing import Any

_TRUE = {"1", "true", "yes", "on"}


def _enabled(value: Any) -> bool:
    return str(value).strip().lower() in _TRUE


async def isAnalyticsDisabled(config: dict[str, Any] | None = None) -> bool:
    """Return true when telemetry should not be collected."""

    config = config or {}
    for key in ("analyticsDisabled", "disableAnalytics", "telemetryDisabled"):
        if key in config:
            return bool(config[key])
    return any(
        _enabled(os.getenv(name))
        for name in (
            "DEEPSEEK_DISABLE_ANALYTICS",
            "DISABLE_ANALYTICS",
            "CLAUDE_CODE_DISABLE_ANALYTICS",
            "DO_NOT_TRACK",
        )
    )


async def isFeedbackSurveyDisabled(config: dict[str, Any] | None = None) -> bool:
    """Return true when feedback prompts should be hidden."""

    config = config or {}
    for key in ("feedbackSurveyDisabled", "disableFeedbackSurvey"):
        if key in config:
            return bool(config[key])
    return _enabled(os.getenv("DEEPSEEK_DISABLE_FEEDBACK_SURVEY") or os.getenv("DISABLE_FEEDBACK_SURVEY"))
