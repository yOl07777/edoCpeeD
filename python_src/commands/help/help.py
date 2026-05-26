"""Help command shim."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


async def call(onDone: DoneCallback | None = None, context: dict[str, Any] | Any = None, *_args: Any) -> dict[str, Any]:
    options = context.get("options", {}) if isinstance(context, dict) else getattr(context, "options", {})
    commands = options.get("commands", []) if isinstance(options, dict) else []
    return {"type": "help", "commands": list(commands or []), "onClose": onDone}
