"""Auto-memory path helpers for the DeepSeek migration."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from python_src.utils.path import sanitizePath

AUTO_MEM_DIRNAME = "memory"
AUTO_MEM_ENTRYPOINT_NAME = "MEMORY.md"


def _env_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _env_falsy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"0", "false", "no", "off"}


def _ensure_trailing_sep(path: Path) -> str:
    return str(path.resolve(strict=False)) + os.sep


def _validate_memory_path(raw: str | None, *, expand_tilde: bool) -> str | None:
    if not raw:
        return None
    candidate = raw.strip()
    if expand_tilde and (candidate.startswith("~/") or candidate.startswith("~\\")):
        rest = candidate[2:]
        rest_norm = os.path.normpath(rest or ".")
        if rest_norm in {".", ".."}:
            return None
        candidate = str(Path.home() / rest)
    path = Path(candidate).expanduser()
    normalized = str(path.resolve(strict=False)).rstrip("\\/")
    if (
        not Path(normalized).is_absolute()
        or len(normalized) < 3
        or normalized[:2].isalpha() and normalized.endswith(":")
        or normalized.startswith("\\\\")
        or normalized.startswith("//")
        or "\0" in normalized
    ):
        return None
    return normalized + os.sep


def isAutoMemoryEnabled(*_args: Any, **_kwargs: Any) -> bool:
    """Return whether local auto-memory should be active."""

    disabled = os.getenv("DEEPSEEK_CODE_DISABLE_AUTO_MEMORY") or os.getenv("CLAUDE_CODE_DISABLE_AUTO_MEMORY")
    if _env_truthy(disabled):
        return False
    if _env_falsy(disabled):
        return True
    if _env_truthy(os.getenv("DEEPSEEK_CODE_SIMPLE") or os.getenv("CLAUDE_CODE_SIMPLE")):
        return False
    if _env_truthy(os.getenv("DEEPSEEK_CODE_REMOTE") or os.getenv("CLAUDE_CODE_REMOTE")) and not (
        os.getenv("DEEPSEEK_CODE_REMOTE_MEMORY_DIR") or os.getenv("CLAUDE_CODE_REMOTE_MEMORY_DIR")
    ):
        return False
    return True


def isExtractModeActive(*_args: Any, **_kwargs: Any) -> bool:
    """Return whether background memory extraction is enabled."""

    return _env_truthy(os.getenv("DEEPSEEK_EXTRACT_MEMORIES") or os.getenv("EXTRACT_MEMORIES"))


def getMemoryBaseDir(*_args: Any, **_kwargs: Any) -> str:
    """Return the base directory for persistent memory storage."""

    return (
        os.getenv("DEEPSEEK_CODE_REMOTE_MEMORY_DIR")
        or os.getenv("CLAUDE_CODE_REMOTE_MEMORY_DIR")
        or os.getenv("DEEPCODE_CONFIG_HOME")
        or os.getenv("DEEPSEEK_CONFIG_DIR")
        or str(Path.home() / ".deepseek")
    )


def _get_auto_mem_path_override() -> str | None:
    return _validate_memory_path(
        os.getenv("DEEPSEEK_COWORK_MEMORY_PATH_OVERRIDE") or os.getenv("CLAUDE_COWORK_MEMORY_PATH_OVERRIDE"),
        expand_tilde=False,
    )


def _get_auto_mem_path_setting() -> str | None:
    return _validate_memory_path(os.getenv("DEEPSEEK_AUTO_MEMORY_DIRECTORY"), expand_tilde=True)


def hasAutoMemPathOverride(*_args: Any, **_kwargs: Any) -> bool:
    return _get_auto_mem_path_override() is not None


def _project_key() -> str:
    return sanitizePath(str(Path.cwd().resolve(strict=False))).strip("/").replace(":", "")


def getAutoMemPath(*_args: Any, **_kwargs: Any) -> str:
    """Return the auto-memory directory path with a trailing separator."""

    override = _get_auto_mem_path_override() or _get_auto_mem_path_setting()
    if override:
        return override
    return _ensure_trailing_sep(Path(getMemoryBaseDir()) / "projects" / _project_key() / AUTO_MEM_DIRNAME)


def getAutoMemDailyLogPath(date: datetime | None = None, *_args: Any, **_kwargs: Any) -> str:
    value = date or datetime.now()
    yyyy = f"{value.year:04d}"
    mm = f"{value.month:02d}"
    dd = f"{value.day:02d}"
    return str(Path(getAutoMemPath()) / "logs" / yyyy / mm / f"{yyyy}-{mm}-{dd}.md")


def getAutoMemEntrypoint(*_args: Any, **_kwargs: Any) -> str:
    return str(Path(getAutoMemPath()) / AUTO_MEM_ENTRYPOINT_NAME)


def isAutoMemPath(absolutePath: str | Path, *_args: Any, **_kwargs: Any) -> bool:
    candidate = str(Path(absolutePath).resolve(strict=False))
    return candidate.startswith(getAutoMemPath().rstrip("\\/") + os.sep)


__all__ = [
    "getAutoMemDailyLogPath",
    "getAutoMemEntrypoint",
    "getAutoMemPath",
    "getMemoryBaseDir",
    "hasAutoMemPathOverride",
    "isAutoMemPath",
    "isAutoMemoryEnabled",
    "isExtractModeActive",
]
