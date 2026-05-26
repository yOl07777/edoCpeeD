from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import HOOK_EVENTS, hook_payload


async def SelectEventMode(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("event") or kwargs.get("selected") or (args[0] if args else "PreToolUse"))
    return hook_payload(
        "select_hook_event_mode",
        selected=selected,
        events=[{"id": event, "selected": event == selected} for event in HOOK_EVENTS],
        valid=selected in HOOK_EVENTS,
    )


__all__ = ["SelectEventMode"]
