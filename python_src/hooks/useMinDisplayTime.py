from __future__ import annotations

from typing import Any

from ._basic import first_mapping, now_ms, pick


async def useMinDisplayTime(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    started_at = int(pick(options, "startedAt", "startTime", "start", default=now_ms()))
    minimum = int(pick(options, "minMs", "minimumMs", "durationMs", default=350))
    current = int(pick(options, "now", "nowMs", default=now_ms()))
    elapsed = max(0, current - started_at)
    remaining = max(0, minimum - elapsed)
    return {
        "provider": "deepseek",
        "ready": remaining == 0,
        "elapsedMs": elapsed,
        "remainingMs": remaining,
        "minMs": minimum,
    }
