"""Release notes cache and parser."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

CHANGELOG_URL = "https://github.com/deepseek-ai/DeepSeek-Coder"
_changelog_memory_cache: str | None = None


def _cache_path() -> Path:
    root = Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode")
    return root / "cache" / "changelog.md"


def _version_tuple(version: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", version)
    return tuple(int(n) for n in nums[:3]) or (0,)


def _resetChangelogCacheForTesting() -> None:
    global _changelog_memory_cache
    _changelog_memory_cache = None


async def fetchAndStoreChangelog(content: str | None = None) -> None:
    global _changelog_memory_cache
    if content is None:
        return
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _changelog_memory_cache = content


async def getStoredChangelog() -> str:
    global _changelog_memory_cache
    if _changelog_memory_cache is not None:
        return _changelog_memory_cache
    try:
        _changelog_memory_cache = _cache_path().read_text(encoding="utf-8")
    except OSError:
        _changelog_memory_cache = ""
    return _changelog_memory_cache


def getStoredChangelogFromMemory() -> str:
    return _changelog_memory_cache or ""


def parseChangelog(content: str) -> dict[str, list[str]]:
    if not content:
        return {}
    notes: dict[str, list[str]] = {}
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)[1:]
    for section in sections:
        lines = [line.rstrip() for line in section.splitlines()]
        if not lines:
            continue
        version = lines[0].split(" - ", 1)[0].strip()
        bullets = [line.strip()[2:].strip() for line in lines[1:] if line.strip().startswith("- ")]
        if version and bullets:
            notes[version] = bullets
    return notes


def getAllReleaseNotes(changelogContent: str | None = None) -> list[tuple[str, list[str]]]:
    parsed = parseChangelog(changelogContent if changelogContent is not None else getStoredChangelogFromMemory())
    return [(version, parsed[version]) for version in sorted(parsed, key=_version_tuple)]


def getRecentReleaseNotes(currentVersion: str, previousVersion: str | None = None, changelogContent: str | None = None) -> list[str]:
    parsed = parseChangelog(changelogContent if changelogContent is not None else getStoredChangelogFromMemory())
    previous = _version_tuple(previousVersion or "0")
    current = _version_tuple(currentVersion)
    output: list[str] = []
    for version in sorted(parsed, key=_version_tuple, reverse=True):
        vt = _version_tuple(version)
        if previous < vt <= current:
            output.extend(parsed[version])
    return output[:5]


async def checkForReleaseNotes(lastSeenVersion: str | None, currentVersion: str = "0.0.0") -> dict[str, Any]:
    changelog = await getStoredChangelog()
    notes = getRecentReleaseNotes(currentVersion, lastSeenVersion, changelog)
    return {"hasReleaseNotes": bool(notes), "releaseNotes": notes}


def checkForReleaseNotesSync(lastSeenVersion: str | None, currentVersion: str = "0.0.0") -> dict[str, Any]:
    notes = getRecentReleaseNotes(currentVersion, lastSeenVersion)
    return {"hasReleaseNotes": bool(notes), "releaseNotes": notes}


async def migrateChangelogFromConfig() -> None:
    return None
