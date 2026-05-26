"""Load markdown-backed configuration from DeepSeek/Claude-style directories."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .frontmatterParser import parseFrontmatter

CLAUDE_CONFIG_DIRECTORIES = ["commands", "agents", "output-styles", "skills", "workflows", "templates"]
_LOAD_CACHE: dict[tuple[str, str], list[dict[str, Any]]] = {}


def extractDescriptionFromMarkdown(content: str, defaultDescription: str = "Custom item") -> str:
    for line in content.splitlines():
        trimmed = line.strip()
        if not trimmed:
            continue
        if trimmed.startswith("#"):
            trimmed = trimmed.lstrip("#").strip()
        return trimmed[:97] + "..." if len(trimmed) > 100 else trimmed
    return defaultDescription


def _split_tools(value: Any) -> list[str] | None:
    if value is None:
        return None
    values = value if isinstance(value, list) else [value]
    tools: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        for piece in item.split(","):
            stripped = piece.strip()
            if stripped:
                tools.append(stripped)
    if "*" in tools:
        return ["*"]
    return tools


def parseAgentToolsFromFrontmatter(toolsValue: Any) -> list[str] | None:
    parsed = _split_tools(toolsValue)
    if parsed is None or "*" in parsed:
        return None
    return parsed


def parseSlashCommandToolsFromFrontmatter(toolsValue: Any) -> list[str]:
    parsed = _split_tools(toolsValue)
    if parsed is None:
        return []
    return parsed


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("CLAUDE_CONFIG_DIR") or Path.home() / ".deepcode")


def getProjectDirsUpToHome(subdir: str, cwd: str | os.PathLike[str]) -> list[str]:
    current = Path(cwd).resolve()
    home = Path.home().resolve()
    dirs: list[str] = []
    while True:
        for config_dir in (".deepseek", ".claude"):
            candidate = current / config_dir / subdir
            if candidate.is_dir():
                dirs.append(str(candidate))
        if current == home or current.parent == current or (current / ".git").exists():
            break
        current = current.parent
    return dirs


def _load_markdown_files(directory: Path, source: str) -> list[dict[str, Any]]:
    if not directory.is_dir():
        return []
    files: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*.md")):
        try:
            parsed = parseFrontmatter(path.read_text(encoding="utf-8", errors="replace"), str(path))
            files.append(
                {
                    "filePath": str(path),
                    "baseDir": str(directory),
                    "frontmatter": parsed["frontmatter"],
                    "content": parsed["content"],
                    "source": source,
                }
            )
        except OSError:
            continue
    return files


async def loadMarkdownFilesForSubdir(subdir: str, cwd: str | os.PathLike[str]) -> list[dict[str, Any]]:
    key = (subdir, str(Path(cwd).resolve()))
    if key in _LOAD_CACHE:
        return [dict(item) for item in _LOAD_CACHE[key]]
    managed_dir = Path(os.getenv("DEEPCODE_MANAGED_CONFIG_HOME") or Path.home() / ".deepcode-managed") / subdir
    user_dir = _config_home() / subdir
    project_dirs = [Path(path) for path in getProjectDirsUpToHome(subdir, cwd)]
    files: list[dict[str, Any]] = []
    files.extend(_load_markdown_files(managed_dir, "policySettings"))
    files.extend(_load_markdown_files(user_dir, "userSettings"))
    for directory in project_dirs:
        files.extend(_load_markdown_files(directory, "projectSettings"))
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in files:
        real = str(Path(item["filePath"]).resolve())
        if real in seen:
            continue
        seen.add(real)
        deduped.append(item)
    _LOAD_CACHE[key] = deduped
    return [dict(item) for item in deduped]


def clearMarkdownConfigLoaderCache() -> None:
    _LOAD_CACHE.clear()
