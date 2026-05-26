from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import file_write_diff, normalize_permission_input


async def FileWriteToolDiff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = normalize_permission_input(*args, **kwargs)
    path = str(data.get("path") or data.get("file_path") or data.get("input_path") or "")
    content = str(data.get("content") or data.get("input_content") or "")
    return file_write_diff(path, content, cwd=data.get("cwd"))


__all__ = ["FileWriteToolDiff"]
