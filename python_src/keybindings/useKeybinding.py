"""Keybinding hook shims for Python runtime tests and adapters."""

from __future__ import annotations

from typing import Any, Callable

from .KeybindingContext import useOptionalKeybindingContext


class InputEvent:
    def __init__(self) -> None:
        self.stopped = False

    def stopImmediatePropagation(self) -> None:
        self.stopped = True


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def handleKeybindingInput(
    action: str,
    handler: Callable[[], Any],
    input: str,
    key: dict[str, Any] | Any,
    *,
    context: str = "Global",
    event: InputEvent | None = None,
) -> dict[str, Any]:
    keybindingContext = useOptionalKeybindingContext()
    if not keybindingContext:
        return {"type": "none", "handled": False}
    contexts = _unique([*keybindingContext.activeContexts, context, "Global"])
    result = keybindingContext.resolve(input, key, contexts)
    handled = False
    if result["type"] == "match":
        keybindingContext.setPendingChord(None)
        if result.get("action") == action:
            handled = handler() is not False
    elif result["type"] == "chord_started":
        keybindingContext.setPendingChord(result["pending"])
        handled = True
    elif result["type"] in {"chord_cancelled", "unbound"}:
        keybindingContext.setPendingChord(None)
        handled = True
    if handled and event:
        event.stopImmediatePropagation()
    return {**result, "handled": handled}


def useKeybinding(action: str, handler: Callable[[], Any], options: dict[str, Any] | None = None) -> Callable[[str, dict[str, Any] | Any, InputEvent | None], dict[str, Any]] | None:
    options = options or {}
    if options.get("isActive", True) is False:
        return None
    context = str(options.get("context", "Global"))
    keybindingContext = useOptionalKeybindingContext()
    if keybindingContext:
        keybindingContext.registerHandler({"action": action, "context": context, "handler": handler})

    def handle(input: str, key: dict[str, Any] | Any, event: InputEvent | None = None) -> dict[str, Any]:
        return handleKeybindingInput(action, handler, input, key, context=context, event=event)

    return handle


def useKeybindings(handlers: dict[str, Callable[[], Any]], options: dict[str, Any] | None = None) -> Callable[[str, dict[str, Any] | Any, InputEvent | None], dict[str, Any]] | None:
    options = options or {}
    if options.get("isActive", True) is False:
        return None
    context = str(options.get("context", "Global"))
    keybindingContext = useOptionalKeybindingContext()
    if keybindingContext:
        for action, handler in handlers.items():
            keybindingContext.registerHandler({"action": action, "context": context, "handler": handler})

    def handle(input: str, key: dict[str, Any] | Any, event: InputEvent | None = None) -> dict[str, Any]:
        keybindingContextInner = useOptionalKeybindingContext()
        if not keybindingContextInner:
            return {"type": "none", "handled": False}
        contexts = _unique([*keybindingContextInner.activeContexts, context, "Global"])
        result = keybindingContextInner.resolve(input, key, contexts)
        handled = False
        if result["type"] == "match":
            keybindingContextInner.setPendingChord(None)
            action = result.get("action")
            if action in handlers:
                handled = handlers[action]() is not False
        elif result["type"] == "chord_started":
            keybindingContextInner.setPendingChord(result["pending"])
            handled = True
        elif result["type"] in {"chord_cancelled", "unbound"}:
            keybindingContextInner.setPendingChord(None)
            handled = True
        if handled and event:
            event.stopImmediatePropagation()
        return {**result, "handled": handled}

    return handle
