"""Implementation for `/color`."""

from __future__ import annotations

from typing import Any, Callable

AGENT_COLORS = ("red", "orange", "yellow", "green", "blue", "purple", "pink")
RESET_ALIASES = {"default", "reset", "none", "gray", "grey"}


async def call(onDone: Callable[..., Any] | None = None, context: dict[str, Any] | None = None, args: str = "") -> dict[str, Any]:
    color_arg = (args or "").strip().lower()
    if not color_arg:
        message = f"Please provide a color. Available colors: {', '.join(AGENT_COLORS)}, default"
        if onDone:
            onDone(message, {"display": "system"})
        return {"ok": False, "message": message, "available": list(AGENT_COLORS)}
    app_state = context.get("appState", context) if isinstance(context, dict) else {}
    standalone = app_state.setdefault("standaloneAgentContext", {}) if isinstance(app_state, dict) else {}
    if color_arg in RESET_ALIASES:
        standalone.pop("color", None)
        message = "Session color reset to default"
        if onDone:
            onDone(message, {"display": "system"})
        return {"ok": True, "color": None, "message": message}
    if color_arg not in AGENT_COLORS:
        message = f'Invalid color "{color_arg}". Available colors: {", ".join(AGENT_COLORS)}, default'
        if onDone:
            onDone(message, {"display": "system"})
        return {"ok": False, "message": message, "available": list(AGENT_COLORS)}
    standalone["color"] = color_arg
    message = f"Session color set to: {color_arg}"
    if onDone:
        onDone(message, {"display": "system"})
    return {"ok": True, "color": color_arg, "message": message}
