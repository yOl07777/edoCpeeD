from __future__ import annotations

from typing import Any


async def CommandKeybindingHandlers(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    bindings = dict(kwargs.get("bindings", {}) or {})
    key = str(kwargs.get("key", ""))
    command = bindings.get(key)
    return {"provider": "deepseek", "bindings": bindings, "key": key, "command": command, "handled": command is not None}


__all__ = ["CommandKeybindingHandlers"]
