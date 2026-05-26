from __future__ import annotations

from typing import Any


async def useInboxPoller(messages: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = list(kwargs.get("messages", messages or []))
    unread = [item for item in rows if not item.get("read")]
    return {"provider": "deepseek", "messages": rows, "unread": unread, "unreadCount": len(unread), "polling": bool(kwargs.get("polling", False))}


__all__ = ["useInboxPoller"]
