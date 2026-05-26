from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from python_src.components.permissions._shared import permission_options


def _path_from_args(*args: Any, **kwargs: Any) -> str:
    if "path" in kwargs and kwargs["path"] is not None:
        return str(kwargs["path"])
    if "file_path" in kwargs and kwargs["file_path"] is not None:
        return str(kwargs["file_path"])
    if args:
        first = args[0]
        if isinstance(first, dict):
            return str(first.get("path") or first.get("file_path") or "")
        return str(first)
    return ""


async def getFilePermissionOptions(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    path = _path_from_args(*args, **kwargs)
    return permission_options("file", path=path or None)


async def isInClaudeFolder(*args: Any, **kwargs: Any) -> bool:
    path = Path(_path_from_args(*args, **kwargs) or ".").expanduser().resolve()
    parts = {part.lower() for part in path.parts}
    return ".claude" in parts or ".deepseek" in parts


async def isInGlobalClaudeFolder(*args: Any, **kwargs: Any) -> bool:
    path = Path(_path_from_args(*args, **kwargs) or ".").expanduser().resolve()
    home = Path(os.path.expanduser("~")).resolve()
    candidates = [
        home / ".claude",
        home / ".deepseek",
        Path(os.getenv("DEEPCODE_CONFIG_HOME", home / ".deepseek")).expanduser().resolve(),
    ]
    return any(path == candidate or candidate in path.parents for candidate in candidates)


__all__ = ["getFilePermissionOptions", "isInClaudeFolder", "isInGlobalClaudeFolder"]
