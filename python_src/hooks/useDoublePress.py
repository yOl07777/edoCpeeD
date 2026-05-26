from __future__ import annotations

import time
from typing import Any


DOUBLE_PRESS_TIMEOUT_MS = 500
_LAST_PRESS: dict[str, float] = {}


async def useDoublePress(key: Any = "default", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    name = str(kwargs.get("key", key) or "default")
    now = float(kwargs.get("now", time.monotonic() * 1000))
    timeout = float(kwargs.get("timeoutMs", DOUBLE_PRESS_TIMEOUT_MS))
    last = _LAST_PRESS.get(name, 0.0)
    double = bool(last and now - last <= timeout)
    _LAST_PRESS[name] = now
    return {"provider": "deepseek", "key": name, "doublePressed": double, "last": last}


__all__ = ["DOUBLE_PRESS_TIMEOUT_MS", "useDoublePress"]
