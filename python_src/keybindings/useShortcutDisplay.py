"""Shortcut display hook shim for Python callers."""

from __future__ import annotations

from typing import Any

from .KeybindingContext import useOptionalKeybindingContext

FALLBACK_EVENTS: list[dict[str, Any]] = []


def useShortcutDisplay(action: str, context: str, fallback: str) -> str:
    keybindingContext = useOptionalKeybindingContext()
    resolved = keybindingContext.getDisplayText(action, context) if keybindingContext else None
    if resolved is not None:
        return resolved
    FALLBACK_EVENTS.append(
        {
            "event": "tengu_keybinding_fallback_used",
            "action": action,
            "context": context,
            "fallback": fallback,
            "reason": "action_not_found" if keybindingContext else "no_context",
        }
    )
    return fallback


def resetShortcutDisplayEventsForTesting() -> None:
    FALLBACK_EVENTS.clear()
