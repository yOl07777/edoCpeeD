from __future__ import annotations

from typing import Any


async def useStalledAnimation(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    elapsed_ms = int(kwargs.get("elapsedMs", kwargs.get("elapsed_ms", 0)) or 0)
    threshold_ms = int(kwargs.get("thresholdMs", kwargs.get("threshold_ms", 30000)) or 30000)
    stalled = elapsed_ms >= threshold_ms
    return {
        "type": "stalled_animation",
        "provider": "deepseek",
        "elapsedMs": elapsed_ms,
        "thresholdMs": threshold_ms,
        "stalled": stalled,
        "message": "Still working" if stalled else "Working",
    }


__all__ = ["useStalledAnimation"]
