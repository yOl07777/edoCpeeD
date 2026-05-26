"""Theme command shim."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


async def call(onDone: DoneCallback | None = None, _context: Any = None, *_args: Any) -> dict[str, Any]:
    return {"type": "theme_picker", "onDone": onDone, "availableThemes": ["light", "dark", "auto"]}


async def selectTheme(setting: str, onDone: DoneCallback | None = None) -> str:
    message = f"Theme set to {setting}"
    if onDone is not None:
        result = onDone(message)
        if hasattr(result, "__await__"):
            await result
    return message
