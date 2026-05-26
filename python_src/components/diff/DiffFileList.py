from __future__ import annotations

from typing import Any

from python_src.components.diff._shared import diff_payload, normalize_file


async def DiffFileList(*args: Any, **kwargs: Any) -> Any:
    files = kwargs.get("files") or (args[0] if args else []) or []
    selected_index = int(kwargs.get("selectedIndex", 0) or 0)
    rows = []
    for index, file in enumerate(files):
        item = normalize_file(file, index)
        item["selected"] = index == selected_index
        rows.append(item)
    return diff_payload("diff_file_list", files=rows, count=len(rows), selectedIndex=selected_index if rows else None)


__all__ = ["DiffFileList"]
