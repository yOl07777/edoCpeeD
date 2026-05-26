from __future__ import annotations

from typing import Any, Callable

from python_src.commands.hooks.index import getHooksStatus


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    status = await getHooksStatus(cwd)
    if args:
        status["filter"] = args
    value = f"DeepSeek hook configuration: {len(status['hookEvents'])} event group(s) configured."
    if onDone:
        onDone(value)
    return {"type": "hooks", "value": value, "status": status}


hooks = {
    "type": "local",
    "name": "hooks",
    "description": "View DeepSeek hook configurations for tool events",
    "immediate": True,
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = hooks


__all__ = ["call", "default", "hooks"]
