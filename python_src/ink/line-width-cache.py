from __future__ import annotations

import importlib
from typing import Any

measureText = importlib.import_module("python_src.ink.measure-text").measureText

_CACHE: dict[str, int] = {}


async def lineWidth(*args: Any, **kwargs: Any) -> Any:
    line = str(args[0] if args else kwargs.get("line", ""))
    if line not in _CACHE:
        _CACHE[line] = measureText(line)
    return _CACHE[line]
