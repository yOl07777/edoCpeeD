from __future__ import annotations

from pathlib import Path
from typing import Any

from python_src.components.memory._shared import memory_payload


async def getRelativeMemoryPath(*args: Any, **kwargs: Any) -> Any:
    path = Path(str(kwargs.get("path") or (args[0] if args else ".deepseek/memory.md")))
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


async def MemoryUpdateNotification(*args: Any, **kwargs: Any) -> Any:
    path = str(kwargs.get("path") or (args[0] if args else ".deepseek/memory.md"))
    changes = kwargs.get("changes") or kwargs.get("updates") or []
    if isinstance(changes, str):
        changes = [changes]
    return memory_payload(
        "memory_update_notification",
        path=path,
        relativePath=await getRelativeMemoryPath(path),
        changes=[str(change) for change in changes],
        count=len(changes),
        message=f"Updated memory at {await getRelativeMemoryPath(path)}",
    )


__all__ = ["MemoryUpdateNotification", "getRelativeMemoryPath"]
