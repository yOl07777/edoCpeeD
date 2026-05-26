from __future__ import annotations

from typing import Any


class CancelRequestHandle:
    def __init__(self) -> None:
        self.cancelled = False
        self.reason = ""

    def cancel(self, reason: str = "cancelled") -> dict[str, Any]:
        self.cancelled = True
        self.reason = reason
        return {"cancelled": self.cancelled, "reason": self.reason}

    def state(self) -> dict[str, Any]:
        return {"cancelled": self.cancelled, "reason": self.reason}


async def CancelRequestHandler(*_args: Any, **kwargs: Any) -> dict[str, Any] | CancelRequestHandle:
    handle = kwargs.get("handle") or CancelRequestHandle()
    if kwargs.get("cancel"):
        return handle.cancel(str(kwargs.get("reason", "cancelled")))
    return handle


__all__ = ["CancelRequestHandle", "CancelRequestHandler"]
