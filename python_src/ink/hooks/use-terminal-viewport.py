from __future__ import annotations

from typing import Any

async def useTerminalViewport(*args: Any, **kwargs: Any) -> Any:
    rows = int(kwargs.get("rows", kwargs.get("height", 24)))
    columns = int(kwargs.get("columns", kwargs.get("width", 80)))
    scroll_top = int(kwargs.get("scrollTop", 0))
    return {"provider": "deepseek", "rows": rows, "columns": columns, "scrollTop": scroll_top}
