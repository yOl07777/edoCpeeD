from __future__ import annotations

from typing import Any


async def emptyFrame(*args: Any, **kwargs: Any) -> Any:
    width = int(kwargs.get("width", args[0] if args else 0))
    height = int(kwargs.get("height", args[1] if len(args) > 1 else 0))
    return "\n".join(" " * width for _ in range(max(0, height)))


async def shouldClearScreen(*args: Any, **kwargs: Any) -> Any:
    previous = args[0] if args else kwargs.get("previous", "")
    current = args[1] if len(args) > 1 else kwargs.get("current", "")
    return "\x1b[2J" in str(current) or len(str(current).splitlines()) < len(str(previous).splitlines())
