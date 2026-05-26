from __future__ import annotations

from typing import Any


async def useLogMessages(messages: list[Any] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = [item if isinstance(item, dict) else {"message": str(item), "level": "info"} for item in kwargs.get("messages", messages or [])]
    level = kwargs.get("level")
    filtered = [row for row in rows if not level or row.get("level") == level]
    return {"provider": "deepseek", "messages": filtered, "count": len(filtered)}


__all__ = ["useLogMessages"]
