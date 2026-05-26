"""Team-memory path validation helpers."""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .paths import getAutoMemPath, isAutoMemoryEnabled


class PathTraversalError(ValueError):
    """Raised when a memory path would escape the team memory directory."""


def _team_feature_enabled() -> bool:
    raw = os.getenv("DEEPSEEK_TEAM_MEMORY_ENABLED") or os.getenv("CLAUDE_TEAM_MEMORY_ENABLED")
    if raw is None:
        return True
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _sanitize_path_key(key: str) -> str:
    if "\0" in key:
        raise PathTraversalError(f'Null byte in path key: "{key}"')
    try:
        decoded = unquote(key)
    except Exception:
        decoded = key
    if decoded != key and (".." in decoded or "/" in decoded or "\\" in decoded):
        raise PathTraversalError(f'URL-encoded traversal in path key: "{key}"')
    normalized = unicodedata.normalize("NFKC", key)
    if normalized != key and (".." in normalized or "/" in normalized or "\\" in normalized or "\0" in normalized):
        raise PathTraversalError(f'Unicode-normalized traversal in path key: "{key}"')
    if "\\" in key:
        raise PathTraversalError(f'Backslash in path key: "{key}"')
    if key.startswith("/") or Path(key).is_absolute():
        raise PathTraversalError(f'Absolute path key: "{key}"')
    if any(part == ".." for part in Path(key).parts):
        raise PathTraversalError(f'Traversal in path key: "{key}"')
    return key


def isTeamMemoryEnabled(*_args: Any, **_kwargs: Any) -> bool:
    return isAutoMemoryEnabled() and _team_feature_enabled()


def getTeamMemPath(*_args: Any, **_kwargs: Any) -> str:
    return str((Path(getAutoMemPath()) / "team").resolve(strict=False)) + os.sep


def getTeamMemEntrypoint(*_args: Any, **_kwargs: Any) -> str:
    return str(Path(getTeamMemPath()) / "MEMORY.md")


def isTeamMemPath(filePath: str | Path, *_args: Any, **_kwargs: Any) -> bool:
    resolved = str(Path(filePath).resolve(strict=False))
    team_dir = getTeamMemPath().rstrip("\\/")
    return resolved == team_dir or resolved.startswith(team_dir + os.sep)


def _validate_real_containment(path: Path) -> None:
    team_dir = Path(getTeamMemPath()).resolve(strict=False)
    existing = path
    tail: list[str] = []
    while not existing.exists() and existing.parent != existing:
        tail.append(existing.name)
        existing = existing.parent
    try:
        real_existing = existing.resolve(strict=True)
    except OSError:
        real_existing = existing.resolve(strict=False)
    real_candidate = real_existing.joinpath(*reversed(tail)).resolve(strict=False)
    try:
        real_team = team_dir.resolve(strict=True)
    except OSError:
        real_team = team_dir.resolve(strict=False)
    if real_candidate != real_team and not str(real_candidate).startswith(str(real_team) + os.sep):
        raise PathTraversalError(f'Path escapes team memory directory via symlink: "{path}"')


async def validateTeamMemWritePath(filePath: str | Path, *_args: Any, **_kwargs: Any) -> str:
    if "\0" in str(filePath):
        raise PathTraversalError(f'Null byte in path: "{filePath}"')
    resolved = Path(filePath).resolve(strict=False)
    if not isTeamMemPath(resolved):
        raise PathTraversalError(f'Path escapes team memory directory: "{filePath}"')
    _validate_real_containment(resolved)
    return str(resolved)


async def validateTeamMemKey(relativeKey: str, *_args: Any, **_kwargs: Any) -> str:
    key = _sanitize_path_key(relativeKey)
    resolved = (Path(getTeamMemPath()) / key).resolve(strict=False)
    if not isTeamMemPath(resolved):
        raise PathTraversalError(f'Key escapes team memory directory: "{relativeKey}"')
    _validate_real_containment(resolved)
    return str(resolved)


def isTeamMemFile(filePath: str | Path, *_args: Any, **_kwargs: Any) -> bool:
    return isTeamMemoryEnabled() and isTeamMemPath(filePath)


__all__ = [
    "PathTraversalError",
    "getTeamMemEntrypoint",
    "getTeamMemPath",
    "isTeamMemFile",
    "isTeamMemPath",
    "isTeamMemoryEnabled",
    "validateTeamMemKey",
    "validateTeamMemWritePath",
]
