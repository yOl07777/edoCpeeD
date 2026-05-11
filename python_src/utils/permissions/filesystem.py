from __future__ import annotations

import fnmatch
import os
import tempfile
from pathlib import Path
from typing import Any


DANGEROUS_DIRECTORIES = {".git", ".svn", ".hg", "node_modules", "__pycache__"}
DANGEROUS_FILES = {".env", ".env.local", "id_rsa", "id_ed25519", "known_hosts"}
getBundledSkillsRoot = lambda: Path.cwd() / "python_src" / "skills" / "bundled"
getClaudeTempDir = lambda: Path(tempfile.gettempdir()) / "deepseek-code"
getResolvedWorkingDirPaths = lambda cwd=None: [Path(cwd or os.getcwd()).resolve()]


def _resolve(path: str | os.PathLike[str], cwd: str | os.PathLike[str] | None = None) -> Path:
    raw = Path(os.path.expanduser(str(path)))
    return (raw if raw.is_absolute() else Path(cwd or os.getcwd()) / raw).resolve(strict=False)


async def toPosixPath(path: str | os.PathLike[str]) -> str:
    return Path(path).as_posix()


async def normalizeCaseForComparison(path: str | os.PathLike[str]) -> str:
    text = str(path).replace("\\", "/")
    return text.lower() if os.name == "nt" else text


async def relativePath(path: str | os.PathLike[str], cwd: str | os.PathLike[str] | None = None) -> str:
    try:
        return str(_resolve(path, cwd).relative_to(Path(cwd or os.getcwd()).resolve()))
    except ValueError:
        return str(_resolve(path, cwd))


async def allWorkingDirectories(cwd: str | os.PathLike[str] | None = None) -> list[str]:
    return [str(path) for path in getResolvedWorkingDirPaths(cwd)]


async def pathInWorkingPath(path: str | os.PathLike[str], cwd: str | os.PathLike[str] | None = None) -> bool:
    resolved = _resolve(path, cwd)
    root = Path(cwd or os.getcwd()).resolve()
    return resolved == root or root in resolved.parents


async def pathInAllowedWorkingPath(
    path: str | os.PathLike[str],
    *,
    cwd: str | os.PathLike[str] | None = None,
    allowed_roots: list[str | os.PathLike[str]] | None = None,
) -> bool:
    resolved = _resolve(path, cwd)
    roots = [Path(item).resolve() for item in (allowed_roots or [cwd or os.getcwd()])]
    return any(resolved == root or root in resolved.parents for root in roots)


async def normalizePatternsToPath(patterns: list[str], cwd: str | os.PathLike[str] | None = None) -> list[str]:
    root = Path(cwd or os.getcwd()).resolve()
    return [str((root / pattern).resolve(strict=False)) if not Path(pattern).is_absolute() else pattern for pattern in patterns]


async def matchingRuleForInput(path: str, patterns: list[str]) -> str | None:
    posix = path.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatchcase(posix, pattern.replace("\\", "/")):
            return pattern
    return None


async def getFileReadIgnorePatterns() -> list[str]:
    return ["**/.git/**", "**/.env*", "**/node_modules/**", "**/__pycache__/**"]


async def isClaudeSettingsPath(path: str | os.PathLike[str]) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    return ".claude/" in normalized or normalized.endswith(".claude.json")


async def checkReadableInternalPath(path: str | os.PathLike[str]) -> dict[str, Any]:
    name = Path(path).name
    if name in DANGEROUS_FILES:
        return {"ok": False, "reason": f"Sensitive file is not readable by default: {name}"}
    return {"ok": True, "reason": None}


async def checkEditableInternalPath(path: str | os.PathLike[str]) -> dict[str, Any]:
    parts = set(Path(path).parts)
    if parts & DANGEROUS_DIRECTORIES or Path(path).name in DANGEROUS_FILES:
        return {"ok": False, "reason": "Path points at an internal or sensitive location."}
    return {"ok": True, "reason": None}


async def checkReadPermissionForTool(path: str, *, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    if not await pathInWorkingPath(path, cwd):
        return {"ok": False, "reason": "Read path is outside the working directory."}
    return await checkReadableInternalPath(path)


async def checkWritePermissionForTool(path: str, *, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    if not await pathInWorkingPath(path, cwd):
        return {"ok": False, "reason": "Write path is outside the working directory."}
    return await checkEditableInternalPath(path)


async def checkPathSafetyForAutoEdit(path: str, *, cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return await checkWritePermissionForTool(path, cwd=cwd)


async def generateSuggestions(path: str) -> list[str]:
    return [f"Allow read_file:{path}", f"Allow write_file:{path}"]


async def getClaudeTempDirName() -> str:
    return "deepseek-code"


async def getProjectTempDir(cwd: str | os.PathLike[str] | None = None) -> str:
    path = Path(cwd or os.getcwd()).resolve() / ".deepseek_tmp"
    path.mkdir(exist_ok=True)
    return str(path)


async def getScratchpadDir(cwd: str | os.PathLike[str] | None = None) -> str:
    path = Path(cwd or os.getcwd()).resolve() / ".deepseek_scratchpad"
    path.mkdir(exist_ok=True)
    return str(path)


async def ensureScratchpadDir(cwd: str | os.PathLike[str] | None = None) -> str:
    return await getScratchpadDir(cwd)


async def isScratchpadEnabled() -> bool:
    return os.getenv("DEEPSEEK_SCRATCHPAD", "1").lower() not in {"0", "false", "no"}


async def getSessionMemoryDir(cwd: str | os.PathLike[str] | None = None) -> str:
    path = Path(cwd or os.getcwd()).resolve() / ".deepseek_memory"
    path.mkdir(exist_ok=True)
    return str(path)


async def getSessionMemoryPath(session_id: str = "default", cwd: str | os.PathLike[str] | None = None) -> str:
    return str(Path(await getSessionMemoryDir(cwd)) / f"{session_id}.md")


async def getClaudeSkillScope(path: str | os.PathLike[str]) -> str:
    normalized = str(path).replace("\\", "/")
    if "/skills/bundled/" in normalized:
        return "bundled"
    if "/.codex/skills/" in normalized or "/.claude/skills/" in normalized:
        return "user"
    return "project"
