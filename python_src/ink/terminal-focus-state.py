from __future__ import annotations

from typing import Any, Callable

_state = {"focused": True}
_subscribers: list[Callable[[bool], Any]] = []


async def getTerminalFocusState(*args: Any, **kwargs: Any) -> Any:
    return {"provider": "deepseek", "focused": _state["focused"], "subscriberCount": len(_subscribers)}


async def getTerminalFocused(*args: Any, **kwargs: Any) -> Any:
    return _state["focused"]


async def setTerminalFocused(*args: Any, **kwargs: Any) -> Any:
    focused = bool(args[0] if args else kwargs.get("focused", True))
    _state["focused"] = focused
    for callback in list(_subscribers):
        callback(focused)
    return focused


async def resetTerminalFocusState(*args: Any, **kwargs: Any) -> Any:
    _state["focused"] = True
    _subscribers.clear()
    return await getTerminalFocusState()


async def subscribeTerminalFocus(*args: Any, **kwargs: Any) -> Any:
    callback = args[0] if args else kwargs.get("callback")
    if callable(callback):
        _subscribers.append(callback)

    def unsubscribe() -> bool:
        if callback in _subscribers:
            _subscribers.remove(callback)
            return True
        return False

    return unsubscribe
