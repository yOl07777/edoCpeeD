from __future__ import annotations

import os
import re
from pathlib import Path


def expandPath(path: str, baseDir: str | None = None) -> str:
    if not isinstance(path, str):
        raise TypeError(f"Path must be a string, received {type(path).__name__}")
    base = Path(baseDir or os.getcwd())
    if "\0" in path or "\0" in str(base):
        raise ValueError("Path contains null bytes")
    trimmed = path.strip()
    if not trimmed:
        return str(base.resolve())
    if trimmed == "~":
        return str(Path.home())
    if trimmed.startswith("~/"):
        return str((Path.home() / trimmed[2:]).resolve(strict=False))
    raw = Path(os.path.expanduser(trimmed))
    return str((raw if raw.is_absolute() else base / raw).resolve(strict=False))


def toRelativePath(absolutePath: str) -> str:
    try:
        rel = os.path.relpath(absolutePath, os.getcwd())
        return absolutePath if rel.startswith("..") else rel
    except ValueError:
        return absolutePath


def getDirectoryForPath(path: str) -> str:
    absolute = Path(expandPath(path))
    if str(absolute).startswith("\\\\") or str(absolute).startswith("//"):
        return str(absolute.parent)
    return str(absolute if absolute.exists() and absolute.is_dir() else absolute.parent)


def containsPathTraversal(path: str) -> bool:
    return bool(re.search(r"(?:^|[\\/])\.\.(?:[\\/]|$)", path))


def sanitizePath(path: str) -> str:
    return path.replace("\0", "").replace("\\", "/")


def normalizePathForConfigKey(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")
