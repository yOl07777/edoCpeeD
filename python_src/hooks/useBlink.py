from __future__ import annotations

import time
from typing import Any


async def useBlink(*_args: Any, **kwargs: Any) -> bool:
    interval = float(kwargs.get("interval", 0.5) or 0.5)
    now = float(kwargs.get("now", time.monotonic()))
    return int(now / max(interval, 0.001)) % 2 == 0


__all__ = ["useBlink"]
