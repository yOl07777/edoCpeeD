"""Shortcut display helpers for non-UI callers."""

from __future__ import annotations

from typing import Any

from .loadUserBindings import loadKeybindingsSync
from .resolver import getBindingDisplayText

LOGGED_FALLBACKS: set[str] = set()
FALLBACK_EVENTS: list[dict[str, Any]] = []


def getShortcutDisplay(action: str, context: str, fallback: str) -> str:
    bindings = loadKeybindingsSync()
    resolved = getBindingDisplayText(action, context, bindings)
    if resolved is not None:
        return resolved
    key = f"{action}:{context}"
    if key not in LOGGED_FALLBACKS:
        LOGGED_FALLBACKS.add(key)
        FALLBACK_EVENTS.append({"event": "tengu_keybinding_fallback_used", "action": action, "context": context, "fallback": fallback, "reason": "action_not_found"})
    return fallback


def resetShortcutFallbackLogForTesting() -> None:
    LOGGED_FALLBACKS.clear()
    FALLBACK_EVENTS.clear()
