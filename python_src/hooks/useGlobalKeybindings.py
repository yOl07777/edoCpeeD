from __future__ import annotations

from typing import Any


async def GlobalKeybindingHandlers(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    bindings = dict(kwargs.get("bindings", {}) or {})
    key = str(kwargs.get("key", ""))
    action = bindings.get(key)
    return {"provider": "deepseek", "key": key, "action": action, "handled": action is not None, "bindings": bindings}


__all__ = ["GlobalKeybindingHandlers"]
