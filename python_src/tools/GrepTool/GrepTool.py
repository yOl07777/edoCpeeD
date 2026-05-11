from __future__ import annotations

import re
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


async def grep_files(
    pattern: str,
    *,
    path: str = ".",
    include: str = "**/*",
    cwd: str | None = None,
    limit: int = 200,
    ignore_case: bool = False,
) -> dict[str, Any]:
    root = resolve_workspace_path(path, cwd=cwd)
    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags)
    matches: list[dict[str, Any]] = []
    for file_path in root.glob(include):
        if len(matches) >= limit:
            break
        if not file_path.is_file():
            continue
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            if regex.search(line):
                matches.append({"path": str(file_path), "line": lineno, "text": line})
                if len(matches) >= limit:
                    break
    return {
        "root": str(root),
        "pattern": pattern,
        "matches": matches,
        "truncated": len(matches) >= limit,
    }


GrepTool = PythonTool(
    name="grep_files",
    description="Search workspace text files with a regular expression.",
    parameters=object_schema(
        {
            "pattern": {"type": "string", "description": "Python regular expression to search for."},
            "path": {"type": "string", "description": "Workspace-relative search root.", "default": "."},
            "include": {"type": "string", "description": "Glob include pattern.", "default": "**/*"},
            "ignore_case": {"type": "boolean", "description": "Case-insensitive search.", "default": False},
            "limit": {"type": "integer", "description": "Maximum number of matches.", "default": 200},
        },
        required=["pattern"],
    ),
    handler=grep_files,
    read_only=True,
)
