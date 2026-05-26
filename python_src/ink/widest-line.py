from __future__ import annotations

import importlib
from typing import Any

measureText = importlib.import_module("python_src.ink.measure-text").measureText


async def widestLine(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    return max((measureText(line) for line in text.splitlines()), default=0)
