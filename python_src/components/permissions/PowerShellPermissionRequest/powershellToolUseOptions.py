from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_options


async def powershellToolUseOptions(*_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    command = kwargs.get("command") or kwargs.get("cmd")
    options = permission_options("powershell")
    for option in options:
        option["command"] = command
        option["shell"] = "powershell"
    return options


__all__ = ["powershellToolUseOptions"]
