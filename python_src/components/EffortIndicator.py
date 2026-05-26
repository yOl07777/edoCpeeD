from __future__ import annotations

from typing import Any

from python_src.components._shared import scalar_arg


_SYMBOLS = {
    "none": "-",
    "minimal": ".",
    "low": "L",
    "medium": "M",
    "high": "H",
    "xhigh": "X",
    "extra": "X",
    "max": "X",
}


async def effortLevelToSymbol(*args: Any, **kwargs: Any) -> Any:
    level = str(kwargs.get("level", scalar_arg(args, "medium"))).lower()
    return _SYMBOLS.get(level, "M")


async def getEffortNotificationText(*args: Any, **kwargs: Any) -> Any:
    level = str(kwargs.get("level", scalar_arg(args, "medium"))).lower()
    if level in {"high", "xhigh", "extra", "max"}:
        return "DeepSeek Code is using deeper reasoning for this task."
    if level in {"minimal", "low"}:
        return "DeepSeek Code is using a lighter reasoning pass."
    return "DeepSeek Code is using balanced reasoning."


__all__ = ["effortLevelToSymbol", "getEffortNotificationText"]
