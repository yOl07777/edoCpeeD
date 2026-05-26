"""Runtime keybinding context container."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .resolver import getBindingDisplayText, resolveKeyWithChordState

Handler = Callable[[], Any]


@dataclass(frozen=True)
class HandlerRegistration:
    action: str
    context: str
    handler: Handler


class KeybindingContextValue:
    def __init__(self, bindings: list[dict[str, Any]]):
        self.bindings = bindings
        self.pendingChord: list[dict[str, Any]] | None = None
        self.activeContexts: set[str] = set()
        self._handlers: dict[str, list[HandlerRegistration]] = {}

    def resolve(self, input: str, key: dict[str, Any] | Any, activeContexts: list[str]) -> dict[str, Any]:
        return resolveKeyWithChordState(input, key, activeContexts, self.bindings, self.pendingChord)

    def setPendingChord(self, pending: list[dict[str, Any]] | None) -> None:
        self.pendingChord = pending

    def getDisplayText(self, action: str, context: str) -> str | None:
        return getBindingDisplayText(action, context, self.bindings)

    def registerActiveContext(self, context: str) -> None:
        self.activeContexts.add(context)

    def unregisterActiveContext(self, context: str) -> None:
        self.activeContexts.discard(context)

    def registerHandler(self, registration: dict[str, Any] | HandlerRegistration) -> Callable[[], None]:
        if isinstance(registration, dict):
            item = HandlerRegistration(str(registration["action"]), str(registration.get("context", "Global")), registration["handler"])
        else:
            item = registration
        self._handlers.setdefault(item.action, []).append(item)

        def unregister() -> None:
            handlers = self._handlers.get(item.action, [])
            self._handlers[item.action] = [existing for existing in handlers if existing is not item]
            if not self._handlers[item.action]:
                self._handlers.pop(item.action, None)

        return unregister

    def invokeAction(self, action: str) -> bool:
        for registration in self._handlers.get(action, []):
            if registration.context in self.activeContexts:
                registration.handler()
                return True
        return False


_current_context: KeybindingContextValue | None = None


def KeybindingProvider(bindings: list[dict[str, Any]], **_: Any) -> KeybindingContextValue:
    global _current_context
    _current_context = KeybindingContextValue(bindings)
    return _current_context


def useKeybindingContext() -> KeybindingContextValue:
    if _current_context is None:
        raise RuntimeError("useKeybindingContext must be used within KeybindingProvider")
    return _current_context


def useOptionalKeybindingContext() -> KeybindingContextValue | None:
    return _current_context


def useRegisterKeybindingContext(context: str, isActive: bool = True) -> Callable[[], None] | None:
    keybindingContext = useOptionalKeybindingContext()
    if not keybindingContext or not isActive:
        return None
    keybindingContext.registerActiveContext(context)

    def unregister() -> None:
        keybindingContext.unregisterActiveContext(context)

    return unregister


def resetKeybindingContextForTesting() -> None:
    global _current_context
    _current_context = None
