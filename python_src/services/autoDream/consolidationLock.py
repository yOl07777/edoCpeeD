"""File lock used by auto-dream memory consolidation."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from python_src.bootstrap.state import getOriginalCwd
from python_src.memdir.paths import getAutoMemPath
from python_src.utils.genericProcessUtils import isProcessRunning
from python_src.utils.listSessionsImpl import listCandidates
from python_src.utils.sessionStoragePortable import getProjectDir


LOCK_FILE = ".consolidate-lock"
HOLDER_STALE_MS = 60 * 60 * 1000


def _lock_path() -> Path:
    return Path(getAutoMemPath()) / LOCK_FILE


async def readLastConsolidatedAt(*_: Any, **__: Any) -> float:
    try:
        return _lock_path().stat().st_mtime * 1000
    except OSError:
        return 0


async def tryAcquireConsolidationLock(*_: Any, **__: Any) -> float | None:
    path = _lock_path()
    mtime_ms: float | None = None
    holder_pid: int | None = None
    try:
        stat = path.stat()
        mtime_ms = stat.st_mtime * 1000
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
        holder_pid = int(raw) if raw else None
    except Exception:
        pass

    if mtime_ms is not None and time.time() * 1000 - mtime_ms < HOLDER_STALE_MS:
        if holder_pid is not None and isProcessRunning(holder_pid):
            return None

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(os.getpid()), encoding="utf-8")
    try:
        if int(path.read_text(encoding="utf-8").strip()) != os.getpid():
            return None
    except Exception:
        return None
    return mtime_ms or 0


async def rollbackConsolidationLock(priorMtime: float, *_: Any, **__: Any) -> None:
    path = _lock_path()
    try:
        if priorMtime == 0:
            path.unlink(missing_ok=True)
            return
        path.write_text("", encoding="utf-8")
        seconds = priorMtime / 1000
        os.utime(path, (seconds, seconds))
    except OSError:
        return


async def recordConsolidation(*_: Any, **__: Any) -> None:
    path = _lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(os.getpid()), encoding="utf-8")


async def listSessionsTouchedSince(sinceMs: float, *_: Any, **__: Any) -> list[str]:
    project_dir = await getProjectDir(getOriginalCwd())
    candidates = await listCandidates(project_dir, True)
    return [item["sessionId"] for item in candidates if item.get("mtime", 0) > sinceMs]


__all__ = [
    "listSessionsTouchedSince",
    "readLastConsolidatedAt",
    "recordConsolidation",
    "rollbackConsolidationLock",
    "tryAcquireConsolidationLock",
]
