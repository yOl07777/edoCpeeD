from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


class FileEditError(RuntimeError):
    pass


async def edit_file(
    path: str,
    old_text: str,
    new_text: str,
    *,
    cwd: str | None = None,
    replace_all: bool = False,
) -> dict[str, Any]:
    target = resolve_workspace_path(path, cwd=cwd)
    if not target.is_file():
        raise FileNotFoundError(str(target))
    content = target.read_text(encoding="utf-8", errors="replace")
    count = content.count(old_text)
    if count == 0:
        raise FileEditError("old_text was not found in the file")
    if count > 1 and not replace_all:
        raise FileEditError("old_text appears multiple times; set replace_all=true")
    updated = content.replace(old_text, new_text) if replace_all else content.replace(old_text, new_text, 1)
    target.write_text(updated, encoding="utf-8")
    return {
        "path": str(target),
        "replacements": count if replace_all else 1,
        "bytes": len(updated.encode("utf-8")),
    }


FileEditTool = PythonTool(
    name="edit_file",
    description="Edit a workspace file by replacing exact text.",
    parameters=object_schema(
        {
            "path": {"type": "string", "description": "Workspace-relative file path."},
            "old_text": {"type": "string", "description": "Exact text to replace."},
            "new_text": {"type": "string", "description": "Replacement text."},
            "replace_all": {"type": "boolean", "description": "Replace all occurrences.", "default": False},
        },
        required=["path", "old_text", "new_text"],
    ),
    handler=edit_file,
    read_only=False,
)
