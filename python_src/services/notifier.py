"""Local notification sink."""

from __future__ import annotations

import time
from typing import Any

_NOTIFICATIONS: list[dict[str, Any]] = []


async def sendNotification(title: str, message: str | None = None, **metadata: Any) -> dict[str, Any]:
    notification = {
        "title": str(title),
        "message": "" if message is None else str(message),
        "metadata": metadata,
        "timestamp": time.time(),
    }
    _NOTIFICATIONS.append(notification)
    return notification


async def getNotifications() -> list[dict[str, Any]]:
    return list(_NOTIFICATIONS)


async def clearNotifications() -> None:
    _NOTIFICATIONS.clear()
