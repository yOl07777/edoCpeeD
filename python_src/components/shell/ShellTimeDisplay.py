from __future__ import annotations

from typing import Any

from python_src.components.shell._shared import format_duration, shell_payload


async def ShellTimeDisplay(*args: Any, **kwargs: Any) -> Any:
    seconds = float(kwargs.get("seconds", kwargs.get("duration", args[0] if args else 0)) or 0)
    return shell_payload("shell_time_display", seconds=seconds, text=format_duration(seconds))


__all__ = ["ShellTimeDisplay"]
