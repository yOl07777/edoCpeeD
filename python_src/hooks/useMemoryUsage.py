from __future__ import annotations

from typing import Any


async def useMemoryUsage(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    used = int(kwargs.get("used", 0) or 0)
    limit = int(kwargs.get("limit", 0) or 0)
    percent = round((used / limit) * 100, 2) if limit > 0 else 0.0
    return {"provider": "deepseek", "used": used, "limit": limit, "percent": percent, "high": percent >= 80}


__all__ = ["useMemoryUsage"]
