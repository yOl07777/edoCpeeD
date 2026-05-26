from __future__ import annotations

from typing import Any


async def useDeferredHookMessages(messages: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = list(kwargs.get("messages", messages or []))
    ready = bool(kwargs.get("ready", True))
    return {"provider": "deepseek", "messages": rows if ready else [], "deferred": [] if ready else rows, "ready": ready}


__all__ = ["useDeferredHookMessages"]
