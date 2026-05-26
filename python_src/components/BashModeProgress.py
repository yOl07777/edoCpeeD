from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def BashModeProgress(*args: Any, **kwargs: Any) -> Any:
    command = str(option(args, kwargs, "command", scalar_arg(args, "")))
    status = str(option(args, kwargs, "status", "running"))
    return component_payload("bash_mode_progress", command=command, status=status, active=status in {"running", "queued"})


__all__ = ["BashModeProgress"]
