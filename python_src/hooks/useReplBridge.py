from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick

BRIDGE_FAILURE_DISMISS_MS: int = 8_000


async def useReplBridge(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    enabled = bool(pick(options, "enabled", default=False))
    error = pick(options, "error", default=None)
    return {
        "provider": "deepseek",
        "enabled": enabled,
        "connected": bool(pick(options, "connected", default=False)) and enabled,
        "error": str(error) if error else None,
        "dismissAfterMs": BRIDGE_FAILURE_DISMISS_MS,
    }
