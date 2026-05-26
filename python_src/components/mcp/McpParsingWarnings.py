from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload


async def McpParsingWarnings(*args: Any, **kwargs: Any) -> Any:
    warnings = kwargs.get("warnings") or (args[0] if args else []) or []
    rows = [str(warning) for warning in warnings]
    return mcp_payload("mcp_parsing_warnings", warnings=rows, count=len(rows), hasWarnings=bool(rows))


__all__ = ["McpParsingWarnings"]
