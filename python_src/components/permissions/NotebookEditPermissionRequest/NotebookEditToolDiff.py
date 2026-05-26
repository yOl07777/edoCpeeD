from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import normalize_permission_input


async def NotebookEditToolDiff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = normalize_permission_input(*args, **kwargs)
    return {
        "type": "notebook_edit_diff",
        "provider": "deepseek",
        "path": data.get("path") or data.get("file_path") or data.get("input_path"),
        "cell": data.get("cell") or data.get("cell_id") or data.get("input_cell"),
        "operation": data.get("operation") or data.get("edit_mode") or "replace",
        "preview": data.get("content") or data.get("new_text") or data.get("input_content") or "",
    }


__all__ = ["NotebookEditToolDiff"]
