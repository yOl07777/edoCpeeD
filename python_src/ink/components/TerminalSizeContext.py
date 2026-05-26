from __future__ import annotations

from typing import Any

TerminalSizeContext: dict[str, Any] = {"provider": "deepseek", "columns": 80, "rows": 24}


def createTerminalSizeContext(**kwargs: Any) -> dict[str, Any]:
    context = dict(TerminalSizeContext)
    context.update(kwargs)
    return context


default = TerminalSizeContext
