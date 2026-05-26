from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_options


async def bashToolUseOptions(*_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    command = kwargs.get("command") or kwargs.get("cmd")
    options = permission_options("shell")
    for option in options:
        option["command"] = command
    return options


__all__ = ["bashToolUseOptions"]
