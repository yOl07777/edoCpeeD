from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


async def write_file(
    path: str,
    content: str,
    *,
    cwd: str | None = None,
    create_dirs: bool = True,
    overwrite: bool = True,
) -> dict[str, Any]:
    target = resolve_workspace_path(path, cwd=cwd)
    if target.exists() and not overwrite:
        raise FileExistsError(str(target))
    if create_dirs:
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {
        "path": str(target),
        "bytes": len(content.encode("utf-8")),
        "written": True,
    }


FileWriteTool = PythonTool(
    name="write_file",
    description="Write UTF-8 text to a file inside the current workspace.",
    parameters=object_schema(
        {
            "path": {"type": "string", "description": "Workspace-relative output path."},
            "content": {"type": "string", "description": "Text content to write."},
            "overwrite": {"type": "boolean", "description": "Whether to overwrite existing files.", "default": True},
        },
        required=["path", "content"],
    ),
    handler=write_file,
    read_only=False,
)
