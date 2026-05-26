from __future__ import annotations

import time
from typing import Any


async def useElapsedTime(start: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    started = float(kwargs.get("start", start if start is not None else time.monotonic()))
    now = float(kwargs.get("now", time.monotonic()))
    elapsed = max(0.0, now - started)
    return {"provider": "deepseek", "seconds": elapsed, "milliseconds": round(elapsed * 1000)}


__all__ = ["useElapsedTime"]
