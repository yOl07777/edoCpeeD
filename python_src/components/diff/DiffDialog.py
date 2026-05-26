from __future__ import annotations

from typing import Any

from python_src.components.diff._shared import diff_payload, normalize_file
from python_src.components.diff.DiffDetailView import DiffDetailView


async def DiffDialog(*args: Any, **kwargs: Any) -> Any:
    files = kwargs.get("files") or (args[0] if args else []) or []
    rows = [normalize_file(file, index) for index, file in enumerate(files)]
    selected_index = max(0, min(int(kwargs.get("selectedIndex", 0) or 0), max(0, len(rows) - 1)))
    detail = await DiffDetailView(rows[selected_index]) if rows else None
    return diff_payload("diff_dialog", files=rows, selectedIndex=selected_index, detail=detail, actions=["accept", "reject", "open"])


__all__ = ["DiffDialog"]
