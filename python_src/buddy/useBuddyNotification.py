"""Notification helpers for companion discovery."""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Callable


def isBuddyTeaserWindow(today: date | None = None, *, internal: bool = False) -> bool:
    if internal:
        return True
    current = today or date.today()
    return current.year == 2026 and current.month == 4 and current.day <= 7


def isBuddyLive(today: date | None = None, *, internal: bool = False) -> bool:
    if internal:
        return True
    current = today or date.today()
    return current.year > 2026 or (current.year == 2026 and current.month >= 4)


def findBuddyTriggerPositions(text: str) -> list[dict[str, int]]:
    return [{"start": match.start(), "end": match.end()} for match in re.finditer(r"/buddy\b", text)]


def useBuddyNotification(
    config: dict[str, Any] | None = None,
    *,
    addNotification: Callable[[dict[str, Any]], Any] | None = None,
    removeNotification: Callable[[str], Any] | None = None,
    today: date | None = None,
) -> dict[str, Any] | None:
    cfg = config or {}
    if cfg.get("companion") or not isBuddyTeaserWindow(today):
        return None
    notification = {"key": "buddy-teaser", "text": "/buddy", "priority": "immediate", "timeoutMs": 15_000}
    if addNotification:
        addNotification(notification)
    return {"notification": notification, "cleanup": (lambda: removeNotification("buddy-teaser")) if removeNotification else None}
