from __future__ import annotations

from typing import Any

from ._basic import first_mapping, now_ms, pick


async def useTimeout(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    started_at = int(pick(options, "start", "startedAt", default=now_ms()))
    timeout = int(pick(options, "timeoutMs", "delay", default=0))
    current = int(pick(options, "now", "nowMs", default=now_ms()))
    elapsed = max(0, current - started_at)
    return {"provider": "deepseek", "elapsedMs": elapsed, "timeoutMs": timeout, "expired": elapsed >= timeout}
