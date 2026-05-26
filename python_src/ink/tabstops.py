from __future__ import annotations

from typing import Any


async def expandTabs(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    tab_size = int(args[1] if len(args) > 1 else kwargs.get("tabSize", kwargs.get("tab_size", 4)))
    result: list[str] = []
    col = 0
    for char in text:
        if char == "\n":
            result.append(char)
            col = 0
        elif char == "\t":
            spaces = tab_size - (col % tab_size)
            result.append(" " * spaces)
            col += spaces
        else:
            result.append(char)
            col += 1
    return "".join(result)
