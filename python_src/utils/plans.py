"""Plan file helpers for plan mode."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

_PLAN_SLUGS: dict[str, str] = {}


def getPlansDirectory(cwd: str | os.PathLike[str] | None = None) -> str:
    root = Path(cwd or os.getenv("DEEPCODE_PROJECT_ROOT") or os.getcwd()).resolve()
    return str(root / ".deepcode" / "plans")


def _session_key(sessionId: str | None = None) -> str:
    return sessionId or os.getenv("DEEPCODE_SESSION_ID") or "default"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "plan"


async def setPlanSlug(slug: str, sessionId: str | None = None) -> str:
    normalized = _slugify(slug)
    _PLAN_SLUGS[_session_key(sessionId)] = normalized
    return normalized


async def getPlanSlug(sessionId: str | None = None) -> str:
    key = _session_key(sessionId)
    if key not in _PLAN_SLUGS:
        _PLAN_SLUGS[key] = _slugify(key)
    return _PLAN_SLUGS[key]


async def clearPlanSlug(sessionId: str | None = None) -> None:
    _PLAN_SLUGS.pop(_session_key(sessionId), None)


async def clearAllPlanSlugs() -> None:
    _PLAN_SLUGS.clear()


async def getPlanFilePath(cwd: str | os.PathLike[str] | None = None, sessionId: str | None = None) -> str:
    directory = Path(getPlansDirectory(cwd))
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / f"{await getPlanSlug(sessionId)}.md")


async def getPlan(cwd: str | os.PathLike[str] | None = None, sessionId: str | None = None) -> str:
    path = Path(await getPlanFilePath(cwd, sessionId))
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


async def copyPlanForFork(sourceSessionId: str, targetSessionId: str, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    source = Path(await getPlanFilePath(cwd, sourceSessionId))
    target_slug = await setPlanSlug(await getPlanSlug(sourceSessionId), targetSessionId)
    target = Path(await getPlanFilePath(cwd, targetSessionId))
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return {"source": str(source), "target": str(target), "slug": target_slug, "copied": source.exists()}


async def copyPlanForResume(sourceSessionId: str, targetSessionId: str, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return await copyPlanForFork(sourceSessionId, targetSessionId, cwd)


async def persistFileSnapshotIfRemote(path: str | os.PathLike[str], content: str | None = None) -> dict[str, Any]:
    file_path = Path(path)
    if content is not None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
    return {"path": str(file_path), "persisted": file_path.exists()}
