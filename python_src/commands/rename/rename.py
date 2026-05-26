"""Local `/rename` command."""

from __future__ import annotations

from typing import Any

from python_src.bootstrap.state import getSessionId
from python_src.utils.config import getCurrentProjectConfig, saveCurrentProjectConfig

from .generateSessionName import generateSessionName


async def getSessionName(session_id: str | None = None) -> str | None:
    config = await getCurrentProjectConfig()
    names = config.get("sessionNames", {})
    return names.get(session_id or getSessionId()) if isinstance(names, dict) else None


async def saveSessionName(name: str, session_id: str | None = None) -> dict[str, Any]:
    sid = session_id or getSessionId()

    def update(config: dict[str, Any]) -> dict[str, Any]:
        names = dict(config.get("sessionNames", {}) if isinstance(config.get("sessionNames"), dict) else {})
        names[sid] = name
        return {**config, "sessionNames": names}

    await saveCurrentProjectConfig(update)
    return {"type": "rename", "sessionId": sid, "name": name}


async def call(onDone: Any = None, _context: Any = None, args: str = "") -> dict[str, Any] | None:
    name = (args or "").strip() or await generateSessionName()
    result = await saveSessionName(name)
    message = f"Session renamed to {name}."
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, **result}
