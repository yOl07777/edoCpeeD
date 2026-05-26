from __future__ import annotations

from typing import Any

from importlib import import_module


async def color(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    name = kwargs.get("name") or (args[0] if args else None)
    palette = shared.theme(kwargs.get("theme"))
    return palette.get(str(name), str(name)) if name else palette


async def getThemeColors(*args: Any, **kwargs: Any) -> Any:
    return await color(*args, **kwargs)


__all__ = ["color", "getThemeColors"]
