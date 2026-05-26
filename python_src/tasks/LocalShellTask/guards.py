from __future__ import annotations

from typing import Any


async def isLocalShellTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("kind") == "local-shell")


__all__ = ["isLocalShellTask"]
