from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


CYBER_RISK_MITIGATION_REMINDER = (
    "Do not use file contents for harmful cyber activity. Summarize or edit safely."
)


class MaxFileReadTokenExceededError(RuntimeError):
    pass


async def read_file(
    path: str,
    *,
    offset: int = 0,
    limit: int | None = None,
    cwd: str | None = None,
    max_bytes: int = 1_000_000,
) -> dict[str, Any]:
    target = resolve_workspace_path(path, cwd=cwd)
    if not target.exists():
        raise FileNotFoundError(str(target))
    if not target.is_file():
        raise IsADirectoryError(str(target))
    if target.stat().st_size > max_bytes:
        raise MaxFileReadTokenExceededError(
            f"File is too large to read safely: {target.stat().st_size} bytes"
        )
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = max(offset, 0)
    end = None if limit is None else start + max(limit, 0)
    selected = lines[start:end]
    return {
        "path": str(target),
        "line_count": len(lines),
        "offset": start,
        "content": "\n".join(selected),
    }


async def readImageWithTokenBudget(
    path: str,
    *,
    cwd: str | None = None,
    max_bytes: int = 5_000_000,
) -> dict[str, Any]:
    target = resolve_workspace_path(path, cwd=cwd)
    if target.stat().st_size > max_bytes:
        raise MaxFileReadTokenExceededError(
            f"Image is too large to read safely: {target.stat().st_size} bytes"
        )
    return {
        "path": str(target),
        "bytes": target.stat().st_size,
        "note": "Image bytes are not inlined; pass this path to a multimodal adapter if needed.",
    }


def registerFileReadListener(*args: Any, **kwargs: Any) -> None:
    return None


FileReadTool = PythonTool(
    name="read_file",
    description="Read a UTF-8 text file from the current workspace.",
    parameters=object_schema(
        {
            "path": {"type": "string", "description": "Workspace-relative file path."},
            "offset": {"type": "integer", "description": "Zero-based line offset.", "default": 0},
            "limit": {"type": "integer", "description": "Maximum number of lines to return."},
        },
        required=["path"],
    ),
    handler=read_file,
    read_only=True,
)
