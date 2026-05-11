from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


async def glob_files(
    pattern: str,
    *,
    path: str = ".",
    cwd: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    root = resolve_workspace_path(path, cwd=cwd)
    matches = sorted(str(p) for p in root.glob(pattern) if p.exists())
    return {
        "root": str(root),
        "pattern": pattern,
        "matches": matches[:limit],
        "truncated": len(matches) > limit,
    }


GlobTool = PythonTool(
    name="glob_files",
    description="Find files by glob pattern within the current workspace.",
    parameters=object_schema(
        {
            "pattern": {"type": "string", "description": "Glob pattern, e.g. **/*.py."},
            "path": {"type": "string", "description": "Workspace-relative search root.", "default": "."},
            "limit": {"type": "integer", "description": "Maximum number of matches.", "default": 200},
        },
        required=["pattern"],
    ),
    handler=glob_files,
    read_only=True,
)
