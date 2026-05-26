"""Small external-store shim migrated from ``src/state/store.ts``."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar


T = TypeVar("T")
Listener = Callable[[], None]
Updater = Callable[[T], T]
OnChange = Callable[[dict[str, T]], None]


@dataclass
class Store(Generic[T]):
    """A minimal synchronous state store matching the TypeScript API."""

    _state: T
    _on_change: OnChange[T] | None = None
    _listeners: set[Listener] = field(default_factory=set)

    def getState(self) -> T:
        return self._state

    def setState(self, updater: Updater[T] | T) -> None:
        old_state = self._state
        next_state = updater(old_state) if callable(updater) else updater
        if next_state is old_state or next_state == old_state:
            return
        self._state = next_state
        if self._on_change is not None:
            self._on_change({"newState": next_state, "oldState": old_state})
        for listener in tuple(self._listeners):
            listener()

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        self._listeners.add(listener)

        def unsubscribe() -> None:
            self._listeners.discard(listener)

        return unsubscribe


def createStore(initialState: T, onChange: OnChange[T] | None = None) -> Store[T]:
    return Store(initialState, onChange)


__all__ = ["Store", "createStore"]
