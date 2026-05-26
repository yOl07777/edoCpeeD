"""Setup helpers for the Python keybinding provider."""

from __future__ import annotations

from typing import Any

from .KeybindingContext import KeybindingContextValue, KeybindingProvider
from .loadUserBindings import initializeKeybindingWatcher, loadKeybindingsSyncWithWarnings, subscribeToKeybindingChanges
from .resolver import resolveKeyWithChordState

CHORD_TIMEOUT_MS = 1000


def summarizeKeybindingWarnings(warnings: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not warnings:
        return None
    error_count = sum(1 for warning in warnings if warning.get("severity") == "error")
    warn_count = sum(1 for warning in warnings if warning.get("severity") == "warning")
    if error_count and warn_count:
        text = f"Found {error_count} keybinding error{'s' if error_count != 1 else ''} and {warn_count} warning{'s' if warn_count != 1 else ''} · /doctor for details"
    elif error_count:
        text = f"Found {error_count} keybinding error{'s' if error_count != 1 else ''} · /doctor for details"
    else:
        text = f"Found {warn_count} keybinding warning{'s' if warn_count != 1 else ''} · /doctor for details"
    return {"key": "keybinding-config-warning", "text": text, "color": "error" if error_count else "warning", "priority": "immediate" if error_count else "high", "timeoutMs": 60000}


class KeybindingSetupState:
    def __init__(self) -> None:
        self.loadResult = loadKeybindingsSyncWithWarnings()
        self.bindings = self.loadResult["bindings"]
        self.warnings = self.loadResult["warnings"]
        self.context = KeybindingProvider(self.bindings)
        self.isReload = False
        self._unsubscribe = subscribeToKeybindingChanges(self.reload)

    def reload(self, result: dict[str, Any] | None = None) -> None:
        self.isReload = True
        self.loadResult = result or loadKeybindingsSyncWithWarnings()
        self.bindings = self.loadResult["bindings"]
        self.warnings = self.loadResult["warnings"]
        self.context.bindings = self.bindings

    def dispose(self) -> None:
        self._unsubscribe()

    def notification(self) -> dict[str, Any] | None:
        return summarizeKeybindingWarnings(self.warnings)


def KeybindingSetup(children: Any = None) -> dict[str, Any]:
    state = KeybindingSetupState()
    return {"type": "keybinding_setup", "children": children, "state": state, "context": state.context}


async def initializeKeybindingSetup() -> KeybindingSetupState:
    await initializeKeybindingWatcher()
    return KeybindingSetupState()


def chordInterceptorHandleInput(
    input: str,
    key: dict[str, Any] | Any,
    *,
    bindings: list[dict[str, Any]],
    pendingChord: list[dict[str, Any]] | None,
    activeContexts: set[str],
    handlerRegistry: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    if (getattr(key, "wheelUp", False) or getattr(key, "wheelDown", False) or (isinstance(key, dict) and (key.get("wheelUp") or key.get("wheelDown")))) and pendingChord is None:
        return {"type": "none", "handled": False, "pending": pendingChord}
    handler_contexts = [registration.get("context") for handlers in handlerRegistry.values() for registration in handlers]
    contexts = list(dict.fromkeys([*handler_contexts, *activeContexts, "Global"]))
    was_in_chord = pendingChord is not None
    result = resolveKeyWithChordState(input, key, contexts, bindings, pendingChord)
    handled = result["type"] in {"chord_started", "chord_cancelled", "unbound"} or (result["type"] == "match" and was_in_chord)
    next_pending = result.get("pending") if result["type"] == "chord_started" else None
    invoked = False
    if result["type"] == "match" and was_in_chord:
        contexts_set = set(contexts)
        for registration in handlerRegistry.get(result.get("action"), []):
            if registration.get("context") in contexts_set:
                registration["handler"]()
                invoked = True
                break
    return {**result, "handled": handled, "pending": next_pending, "invoked": invoked}
