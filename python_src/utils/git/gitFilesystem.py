from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from python_src.utils.git.gitConfigParser import parseConfigString


_GIT_DIR_CACHE: dict[Path, Path | None] = {}


def _repo_root(start: str | os.PathLike[str] | None = None) -> Path:
    return Path(start or os.getcwd()).resolve()


async def clearResolveGitDirCache() -> None:
    _GIT_DIR_CACHE.clear()


async def resolveGitDir(cwd: str | os.PathLike[str] | None = None) -> str | None:
    start = _repo_root(cwd)
    if start in _GIT_DIR_CACHE:
        cached = _GIT_DIR_CACHE[start]
        return str(cached) if cached else None
    for directory in [start, *start.parents]:
        git_path = directory / ".git"
        if git_path.is_dir():
            _GIT_DIR_CACHE[start] = git_path
            return str(git_path)
        if git_path.is_file():
            text = git_path.read_text(encoding="utf-8", errors="replace").strip()
            if text.lower().startswith("gitdir:"):
                raw = text.split(":", 1)[1].strip()
                resolved = Path(raw)
                if not resolved.is_absolute():
                    resolved = directory / resolved
                _GIT_DIR_CACHE[start] = resolved.resolve(strict=False)
                return str(_GIT_DIR_CACHE[start])
    _GIT_DIR_CACHE[start] = None
    return None


async def getCommonDir(git_dir: str | os.PathLike[str] | None = None, cwd: str | os.PathLike[str] | None = None) -> str | None:
    raw = Path(git_dir) if git_dir else Path(await resolveGitDir(cwd) or "")
    if not raw:
        return None
    common_file = raw / "commondir"
    if common_file.exists():
        text = common_file.read_text(encoding="utf-8", errors="replace").strip()
        common = Path(text)
        return str((common if common.is_absolute() else raw / common).resolve(strict=False))
    return str(raw.resolve(strict=False))


async def readRawSymref(path: str | os.PathLike[str]) -> str | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    text = file_path.read_text(encoding="utf-8", errors="replace").strip()
    if text.startswith("ref: "):
        return text[5:].strip()
    return None


async def readGitHead(git_dir: str | os.PathLike[str] | None = None, cwd: str | os.PathLike[str] | None = None) -> str | None:
    resolved = git_dir or await resolveGitDir(cwd)
    if not resolved:
        return None
    head = Path(resolved) / "HEAD"
    if not head.exists():
        return None
    return head.read_text(encoding="utf-8", errors="replace").strip()


async def isValidGitSha(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", value or ""))


async def isSafeRefName(value: str) -> bool:
    if not value or value.startswith("/") or value.endswith("/") or ".." in value or "@{" in value:
        return False
    if any(ch in value for ch in "\\ ~^:?*["):
        return False
    return not value.endswith(".lock")


async def resolveRef(ref: str, git_dir: str | os.PathLike[str] | None = None, cwd: str | os.PathLike[str] | None = None) -> str | None:
    if await isValidGitSha(ref):
        return ref
    if not await isSafeRefName(ref):
        return None
    resolved = git_dir or await resolveGitDir(cwd)
    if not resolved:
        return None
    common = Path(await getCommonDir(resolved) or resolved)
    candidates = [common / ref, common / "refs" / "heads" / ref, common / "refs" / "tags" / ref]
    for candidate in candidates:
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8", errors="replace").strip()
            return text if await isValidGitSha(text) else None
    packed = common / "packed-refs"
    if packed.exists():
        for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            sha, _, name = line.partition(" ")
            if name.strip() == ref and await isValidGitSha(sha):
                return sha
    return None


async def readWorktreeHeadSha(cwd: str | os.PathLike[str] | None = None) -> str | None:
    git_dir = await resolveGitDir(cwd)
    head = await readGitHead(git_dir)
    if not head:
        return None
    if await isValidGitSha(head):
        return head
    if head.startswith("ref: "):
        return await resolveRef(head[5:].strip(), git_dir)
    return None


async def getHeadForDir(cwd: str | os.PathLike[str] | None = None) -> dict[str, str | None]:
    head = await readGitHead(cwd=cwd)
    branch = None
    sha = None
    if head and head.startswith("ref: "):
        ref = head[5:].strip()
        branch = ref.removeprefix("refs/heads/")
        sha = await resolveRef(ref, cwd=cwd)
    elif head and await isValidGitSha(head):
        sha = head
    return {"head": head, "branch": branch, "sha": sha}


async def getCachedHead(cwd: str | os.PathLike[str] | None = None) -> str | None:
    return (await getHeadForDir(cwd)).get("sha")


async def getCachedBranch(cwd: str | os.PathLike[str] | None = None) -> str | None:
    return (await getHeadForDir(cwd)).get("branch")


async def getRemoteUrlForDir(cwd: str | os.PathLike[str] | None = None, remote: str = "origin") -> str | None:
    git_dir = await resolveGitDir(cwd)
    if not git_dir:
        return None
    config_path = Path(git_dir) / "config"
    if not config_path.exists():
        return None
    parsed = await parseConfigString(config_path.read_text(encoding="utf-8", errors="replace"))
    section = parsed.get(f"remote.{remote}", {})
    url = section.get("url")
    return str(url) if url else None


async def getCachedRemoteUrl(cwd: str | os.PathLike[str] | None = None) -> str | None:
    return await getRemoteUrlForDir(cwd)


async def getCachedDefaultBranch(cwd: str | os.PathLike[str] | None = None) -> str | None:
    git_dir = await resolveGitDir(cwd)
    if not git_dir:
        return None
    for ref in ("refs/remotes/origin/HEAD", "refs/heads/main", "refs/heads/master"):
        path = Path(git_dir) / ref
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text.startswith("ref: "):
                return text.rsplit("/", 1)[-1]
            return ref.rsplit("/", 1)[-1]
    return None


async def isShallowClone(cwd: str | os.PathLike[str] | None = None) -> bool:
    git_dir = await resolveGitDir(cwd)
    return bool(git_dir and (Path(git_dir) / "shallow").exists())


async def getWorktreeCountFromFs(cwd: str | os.PathLike[str] | None = None) -> int:
    git_dir = await resolveGitDir(cwd)
    if not git_dir:
        return 0
    common = Path(await getCommonDir(git_dir) or git_dir)
    worktrees = common / "worktrees"
    return len([item for item in worktrees.iterdir() if item.is_dir()]) + 1 if worktrees.exists() else 1


async def resetGitFileWatcher() -> None:
    return None
