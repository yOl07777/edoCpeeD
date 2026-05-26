from __future__ import annotations

from typing import Any


async def useMailboxBridge(messages: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = list(kwargs.get("messages", messages or []))
    return {"provider": "deepseek", "connected": bool(kwargs.get("connected", False)), "pending": rows, "count": len(rows)}


__all__ = ["useMailboxBridge"]
