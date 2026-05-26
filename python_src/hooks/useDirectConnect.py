from __future__ import annotations

from typing import Any


async def useDirectConnect(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    endpoint = str(kwargs.get("endpoint", ""))
    enabled = bool(kwargs.get("enabled", bool(endpoint)))
    return {"provider": "deepseek", "enabled": enabled, "endpoint": endpoint, "connected": bool(kwargs.get("connected", False))}


__all__ = ["useDirectConnect"]
