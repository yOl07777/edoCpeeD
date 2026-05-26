from __future__ import annotations

from typing import Any


async def generateShellSuggestionsLabel(*args: Any, **kwargs: Any) -> str:
    command = str(kwargs.get("command") or kwargs.get("cmd") or (args[0] if args else "")).strip()
    if not command:
        return "Review shell command permission suggestions"
    prefix = command.split()[0] if command.split() else command
    return f"Review permission suggestions for `{prefix}`"


__all__ = ["generateShellSuggestionsLabel"]
