"""Local `/files` command."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _cache_keys(read_file_state: Any) -> list[str]:
    if not read_file_state:
        return []
    if isinstance(read_file_state, dict):
        return [str(key) for key in read_file_state.keys()]
    keys = getattr(read_file_state, "keys", None)
    if callable(keys):
        return [str(key) for key in keys()]
    files = getattr(read_file_state, "files", None)
    if isinstance(files, dict):
        return [str(key) for key in files.keys()]
    if isinstance(files, list):
        return [str(item) for item in files]
    return []


async def call(_args: str | None = None, context: dict[str, Any] | Any = None) -> dict[str, str]:
    read_file_state = None
    if isinstance(context, dict):
        read_file_state = context.get("readFileState")
    else:
        read_file_state = getattr(context, "readFileState", None)

    files = sorted(_cache_keys(read_file_state))
    if not files:
        return {"type": "text", "value": "No files in context"}

    cwd = Path(os.getcwd())
    display = []
    for file in files:
        path = Path(file)
        try:
            display.append(str(path.resolve().relative_to(cwd)))
        except Exception:
            display.append(str(path))
    return {"type": "text", "value": "Files in context:\n" + "\n".join(display)}
