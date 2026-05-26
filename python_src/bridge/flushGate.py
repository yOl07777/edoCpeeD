"""State machine for gating bridge writes during an initial flush."""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class FlushGate(Generic[T]):
    """Queue new items while a historical bridge flush is in progress."""

    def __init__(self) -> None:
        self._active = False
        self._pending: list[T] = []

    @property
    def active(self) -> bool:
        return self._active

    @property
    def pendingCount(self) -> int:
        return len(self._pending)

    def start(self) -> None:
        self._active = True

    def end(self) -> list[T]:
        self._active = False
        pending = list(self._pending)
        self._pending.clear()
        return pending

    def enqueue(self, *items: T) -> bool:
        if not self._active:
            return False
        self._pending.extend(items)
        return True

    def drop(self) -> int:
        self._active = False
        count = len(self._pending)
        self._pending.clear()
        return count

    def deactivate(self) -> None:
        self._active = False
