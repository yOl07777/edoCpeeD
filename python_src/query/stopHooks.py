"""Stop-hook shim for the Python query loop.

The full TypeScript implementation coordinates UI progress messages, teammate
hooks, analytics, prompt suggestions, and background memory extraction.  The
DeepSeek Python migration keeps a safe no-op async-iterable surface so query
orchestration can call it without pulling Claude-specific runtime graphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StopHookResult:
    blockingErrors: list[Any] = field(default_factory=list)
    preventContinuation: bool = False


class StopHookIterator:
    def __init__(self, result: StopHookResult | None = None) -> None:
        self.result = result or StopHookResult()

    def __aiter__(self) -> "StopHookIterator":
        return self

    async def __anext__(self) -> Any:
        raise StopAsyncIteration


def handleStopHooks(*_args: Any, **_kwargs: Any) -> StopHookIterator:
    """Return an empty async iterator with a DeepSeek-safe stop-hook result."""

    return StopHookIterator()


__all__ = ["StopHookIterator", "StopHookResult", "handleStopHooks"]
