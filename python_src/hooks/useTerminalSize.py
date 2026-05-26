from __future__ import annotations

import shutil
from typing import Any

from ._basic import first_mapping, pick


async def useTerminalSize(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    fallback = shutil.get_terminal_size((80, 24))
    columns = int(pick(options, "columns", "width", default=fallback.columns))
    rows = int(pick(options, "rows", "height", default=fallback.lines))
    return {"provider": "deepseek", "columns": columns, "rows": rows, "isNarrow": columns < 80}
