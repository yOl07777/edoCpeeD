from __future__ import annotations

from typing import Any

from python_src.components.memory._shared import memory_payload, normalize_memory_file


async def MemoryFileSelector(*args: Any, **kwargs: Any) -> Any:
    files = kwargs.get("files") or (args[0] if args else []) or [".deepseek/memory.md"]
    selected = str(kwargs.get("selected") or kwargs.get("path") or "")
    rows = [normalize_memory_file(file, index, selected) for index, file in enumerate(files)]
    if selected and not any(row["selected"] for row in rows):
        rows.insert(0, normalize_memory_file(selected, 0, selected))
    return memory_payload("memory_file_selector", files=rows, count=len(rows), selected=selected or (rows[0]["path"] if rows else None))


__all__ = ["MemoryFileSelector"]
