from __future__ import annotations

import fnmatch
import os
from pathlib import Path


async def getGlobalGitignorePath() -> str | None:
    config = os.getenv("GIT_IGNORE_GLOBAL")
    if config:
        return config
    home = Path.home()
    for candidate in (home / ".config" / "git" / "ignore", home / ".gitignore_global"):
        try:
            if candidate.exists():
                return str(candidate)
        except OSError:
            continue
    return None


def _read_patterns(path: Path) -> list[str]:
    try:
        if not path.exists():
            return []
    except OSError:
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.append(stripped)
    return patterns


async def isPathGitignored(path: str | os.PathLike[str], *, cwd: str | os.PathLike[str] | None = None) -> bool:
    root = Path(cwd or os.getcwd()).resolve()
    target = Path(path)
    resolved = (target if target.is_absolute() else root / target).resolve(strict=False)
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError:
        rel = resolved.as_posix()

    patterns = _read_patterns(root / ".gitignore")
    global_path = await getGlobalGitignorePath()
    if global_path:
        patterns += _read_patterns(Path(global_path))
    for pattern in patterns:
        negated = pattern.startswith("!")
        clean = pattern[1:] if negated else pattern
        clean = clean.rstrip("/")
        matched = fnmatch.fnmatchcase(rel, clean) or fnmatch.fnmatchcase(Path(rel).name, clean)
        if matched:
            return not negated
    return False


async def addFileGlobRuleToGitignore(
    pattern: str,
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, object]:
    root = Path(cwd or os.getcwd()).resolve()
    path = root / ".gitignore"
    existing = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    if pattern not in existing:
        existing.append(pattern)
        path.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")
        return {"added": True, "path": str(path), "pattern": pattern}
    return {"added": False, "path": str(path), "pattern": pattern}
