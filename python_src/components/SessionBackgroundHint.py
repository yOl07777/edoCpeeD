from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def SessionBackgroundHint(*args: Any, **kwargs: Any) -> Any:
    running = bool(option(args, kwargs, "running", option(args, kwargs, "background", False)))
    return component_payload("session_background_hint", running=running, text="Session continues in background" if running else "Session is foreground only")


__all__ = ["SessionBackgroundHint"]
