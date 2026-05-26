from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import normalize_permission_input, unified_diff


async def createSingleEditDiffConfig(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = normalize_permission_input(*args, **kwargs)
    path = str(data.get("path") or data.get("file_path") or data.get("input_path") or "")
    old_text = str(data.get("old_text") or data.get("oldText") or data.get("input_old_text") or "")
    new_text = str(data.get("new_text") or data.get("newText") or data.get("input_new_text") or "")
    return {
        "type": "single_edit_diff_config",
        "provider": "deepseek",
        "path": path,
        "diff": unified_diff(old_text, new_text, fromfile=f"{path}:before", tofile=f"{path}:after"),
    }


__all__ = ["createSingleEditDiffConfig"]
