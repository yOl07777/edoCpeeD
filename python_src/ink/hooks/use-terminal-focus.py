from __future__ import annotations

from typing import Any

async def useTerminalFocus(*args: Any, **kwargs: Any) -> Any:
    focused = bool(kwargs.get("focused", kwargs.get("isFocused", True)))
    return {"provider": "deepseek", "isFocused": focused}
