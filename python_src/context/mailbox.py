from __future__ import annotations

from collections import deque
from typing import Any


_MAILBOX: deque[dict[str, Any]] = deque()


async def MailboxProvider(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("clear"):
        _MAILBOX.clear()
    messages = kwargs.get("messages", args[0] if args else None)
    if messages:
        for item in messages:
            _MAILBOX.append(dict(item) if isinstance(item, dict) else {"text": str(item)})
    return await useMailbox()


async def useMailbox(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if "send" in kwargs:
        item = kwargs["send"]
        _MAILBOX.append(dict(item) if isinstance(item, dict) else {"text": str(item)})
    next_item = _MAILBOX.popleft() if kwargs.get("receive") and _MAILBOX else None
    return {"provider": "deepseek", "messages": list(_MAILBOX), "count": len(_MAILBOX), "next": next_item}


__all__ = ["MailboxProvider", "useMailbox"]
