from __future__ import annotations

from typing import Any


async def useExitOnCtrlCD(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    key = str(kwargs.get("key", "")).lower()
    count = int(kwargs.get("count", 1) or 1)
    should_exit = key in {"ctrl+c", "\x03", "c"} and bool(kwargs.get("ctrl", key != "c")) and count >= int(kwargs.get("required", 1) or 1)
    return {"provider": "deepseek", "shouldExit": should_exit, "count": count}


__all__ = ["useExitOnCtrlCD"]
