from __future__ import annotations

from typing import Any

from ._basic import first_mapping, now_ms, pick

DEFAULT_INTERACTION_THRESHOLD_MS: int = 30_000


async def useNotifyAfterTimeout(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    started_at = int(pick(options, "startedAt", "startTime", "start", default=now_ms()))
    threshold = int(pick(options, "thresholdMs", "timeoutMs", default=DEFAULT_INTERACTION_THRESHOLD_MS))
    current = int(pick(options, "now", "nowMs", default=now_ms()))
    elapsed = max(0, current - started_at)
    notify = elapsed >= threshold and not bool(pick(options, "dismissed", default=False))
    return {
        "provider": "deepseek",
        "notify": notify,
        "elapsedMs": elapsed,
        "thresholdMs": threshold,
        "message": pick(options, "message", default="DeepSeek Code is still working."),
    }
