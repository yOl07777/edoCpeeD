from __future__ import annotations

from typing import Any

async def useDeclaredCursor(*args: Any, **kwargs: Any) -> Any:
    row = int(kwargs.get("row", args[0] if args else 0))
    col = int(kwargs.get("col", args[1] if len(args) > 1 else 0))
    visible = bool(kwargs.get("visible", True))
    setter = kwargs.get("setCursor")
    cursor = {"provider": "deepseek", "row": row, "col": col, "visible": visible}
    if callable(setter):
        setter(cursor)
    return cursor
