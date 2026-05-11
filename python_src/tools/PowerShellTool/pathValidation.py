from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from python_src.tools.PowerShellTool.gitSafety import isDotGitPathPS, isGitInternalPathPS


_PATH_ARG_RE = re.compile(r"(?:-Path|-LiteralPath)\s+(['\"]?)([^'\"\s]+)\1", re.IGNORECASE)
_REMOVE_RE = re.compile(r"\b(Remove-Item|rm|del|erase)\b", re.IGNORECASE)


def isDangerousRemovalRawPath(path: str) -> bool:
    cleaned = path.strip("'\"").replace("\\", "/").lower()
    return cleaned in {"", ".", "./", "/", "c:/", "~"} or isDotGitPathPS(cleaned) or isGitInternalPathPS(cleaned)


def dangerousRemovalDeny(command: str) -> str | None:
    if not _REMOVE_RE.search(command):
        return None
    paths = [match.group(2) for match in _PATH_ARG_RE.finditer(command)]
    if not paths:
        tail = _REMOVE_RE.split(command, maxsplit=1)[-1].strip()
        if tail:
            paths = [tail.split()[0]]
    for path in paths:
        if isDangerousRemovalRawPath(path):
            return f"Refusing dangerous removal path: {path}"
    return None


def _extract_paths(command: str) -> list[str]:
    paths = [match.group(2) for match in _PATH_ARG_RE.finditer(command)]
    if paths:
        return paths
    tokens = command.replace(";", " ").split()
    return [token.strip("'\"") for token in tokens if "\\" in token or "/" in token or token.startswith(".")]


def checkPathConstraints(
    command: str,
    *,
    cwd: str | os.PathLike[str] | None = None,
    allowed_roots: list[str | os.PathLike[str]] | None = None,
) -> dict[str, Any]:
    denial = dangerousRemovalDeny(command)
    root = Path(cwd or os.getcwd()).resolve()
    roots = [Path(path).resolve() for path in (allowed_roots or [root])]
    denied: list[str] = []
    for raw_path in _extract_paths(command):
        path = Path(os.path.expanduser(raw_path))
        resolved = (path if path.is_absolute() else root / path).resolve(strict=False)
        if not any(resolved == allowed or allowed in resolved.parents for allowed in roots):
            denied.append(raw_path)
    return {"ok": denial is None and not denied, "reason": denial, "denied_paths": denied}
