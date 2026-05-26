from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def MarkdownTable(*args: Any, **kwargs: Any) -> Any:
    rows = option(args, kwargs, "rows", scalar_arg(args, []))
    if isinstance(rows, str):
        lines = [line.strip() for line in rows.splitlines() if "|" in line]
        parsed = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
        headers = parsed[0] if parsed else []
        body = [line for line in parsed[2:] if line] if len(parsed) > 2 else parsed[1:]
    else:
        body = normalize_items(rows)
        headers = list(body[0].keys()) if body and isinstance(body[0], dict) else []
    return component_payload("markdown_table", headers=headers, rows=body, rowCount=len(body))


__all__ = ["MarkdownTable"]
