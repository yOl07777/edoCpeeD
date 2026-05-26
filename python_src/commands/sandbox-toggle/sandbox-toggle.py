"""Sandbox toggle command shim."""

from __future__ import annotations

import re
from typing import Any, Callable

from python_src.utils.config import getCurrentProjectConfig, saveCurrentProjectConfig


def _emit(onDone: Callable[..., Any] | None, message: str) -> None:
    if not callable(onDone):
        return
    try:
        onDone(message)
    except TypeError:
        onDone(message, {"display": "system"})


def _clean_pattern(pattern: str) -> str:
    return re.sub(r"""^["']|["']$""", "", pattern.strip())


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any] | None:
    trimmed = (args or "").strip()
    config = await getCurrentProjectConfig()
    sandbox = dict(config.get("sandbox") or {})
    excluded = list(sandbox.get("excludedCommands") or [])

    if not trimmed:
        return {"type": "sandbox_settings", "enabled": bool(sandbox.get("enabled", False)), "excludedCommands": excluded}

    parts = trimmed.split(" ", 1)
    subcommand = parts[0].lower()
    if subcommand == "exclude":
        pattern = _clean_pattern(parts[1] if len(parts) > 1 else "")
        if not pattern:
            message = 'Error: Please provide a command pattern to exclude (e.g., /sandbox exclude "npm run test:*")'
            _emit(onDone, message)
            return None
        if pattern not in excluded:
            excluded.append(pattern)
        sandbox["excludedCommands"] = excluded
        await saveCurrentProjectConfig({"sandbox": sandbox})
        message = f'Added "{pattern}" to excluded commands in .deepcode/project.json'
        _emit(onDone, message)
        return {"type": "sandbox_settings", "excluded": pattern, "excludedCommands": excluded}
    if subcommand in {"on", "enable"}:
        sandbox["enabled"] = True
        await saveCurrentProjectConfig({"sandbox": sandbox})
        _emit(onDone, "Sandboxing enabled")
        return {"type": "sandbox_settings", "enabled": True, "excludedCommands": excluded}
    if subcommand in {"off", "disable"}:
        sandbox["enabled"] = False
        await saveCurrentProjectConfig({"sandbox": sandbox})
        _emit(onDone, "Sandboxing disabled")
        return {"type": "sandbox_settings", "enabled": False, "excludedCommands": excluded}

    message = f'Error: Unknown subcommand "{subcommand}". Available subcommands: exclude, on, off'
    _emit(onDone, message)
    return None
