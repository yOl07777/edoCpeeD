from __future__ import annotations

from typing import Any


async def drainStdin(*args: Any, **kwargs: Any) -> Any:
    stdin = args[0] if args else kwargs.get("stdin")
    if stdin is not None and hasattr(stdin, "read"):
        data = stdin.read()
        return data or ""
    return kwargs.get("input", "")
