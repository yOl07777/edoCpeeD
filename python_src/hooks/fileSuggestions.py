from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable


_PATH_CACHE: dict[str, list[str]] = {}
onIndexBuildComplete: list[Callable[[list[str]], Any]] = []


def _root(cwd: Any = None) -> Path:
    return Path(str(cwd or Path.cwd())).resolve()


async def findLongestCommonPrefix(paths: list[str] | tuple[str, ...] | None = None, *_args: Any, **_kwargs: Any) -> str:
    values = [str(path) for path in (paths or [])]
    if not values:
        return ""
    prefix = values[0]
    for value in values[1:]:
        while not value.startswith(prefix) and prefix:
            prefix = prefix[:-1]
    return prefix


async def pathListSignature(paths: list[str] | tuple[str, ...] | None = None, *_args: Any, **_kwargs: Any) -> str:
    payload = "\n".join(sorted(str(path) for path in (paths or [])))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


async def getPathsForSuggestions(cwd: Any = None, *_args: Any, **kwargs: Any) -> list[str]:
    root = _root(kwargs.get("cwd", cwd))
    limit = int(kwargs.get("limit", 500) or 500)
    include_dirs = bool(kwargs.get("include_dirs", True))
    key = f"{root}:{limit}:{include_dirs}"
    if key in _PATH_CACHE and not kwargs.get("refresh"):
        return list(_PATH_CACHE[key])
    paths: list[str] = []
    if root.exists():
        for path in root.rglob("*"):
            if len(paths) >= limit:
                break
            if any(part in {".git", "__pycache__", ".venv", "node_modules"} for part in path.parts):
                continue
            if path.is_file() or (include_dirs and path.is_dir()):
                paths.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    _PATH_CACHE[key] = paths
    return list(paths)


async def getDirectoryNames(cwd: Any = None, *_args: Any, **kwargs: Any) -> list[str]:
    root = _root(kwargs.get("cwd", cwd))
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir() and not path.name.startswith("."))


async def getDirectoryNamesAsync(*args: Any, **kwargs: Any) -> list[str]:
    return await getDirectoryNames(*args, **kwargs)


async def generateFileSuggestions(prefix: Any = "", *_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    query = str(kwargs.get("prefix", prefix) or "").lstrip("@")
    paths = kwargs.get("paths")
    if paths is None:
        paths = await getPathsForSuggestions(kwargs.get("cwd"), limit=kwargs.get("limit", 500))
    matches = [str(path) for path in paths if not query or str(path).lower().startswith(query.lower()) or query.lower() in str(path).lower()]
    return [{"type": "file", "value": path, "label": f"@{path}"} for path in matches[: int(kwargs.get("limit", 20) or 20)]]


async def applyFileSuggestion(input_text: Any = "", suggestion: Any = "", *_args: Any, **kwargs: Any) -> str:
    text = str(kwargs.get("input", input_text) or "")
    value = str(kwargs.get("suggestion", suggestion) or "")
    token = f"@{value.lstrip('@')}"
    if "@" in text:
        head = text[: text.rfind("@")]
        return f"{head}{token}"
    return f"{text}{token}"


async def clearFileSuggestionCaches(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    count = len(_PATH_CACHE)
    _PATH_CACHE.clear()
    return {"provider": "deepseek", "cleared": count}


async def startBackgroundCacheRefresh(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    paths = await getPathsForSuggestions(kwargs.get("cwd"), refresh=True, limit=kwargs.get("limit", 500))
    for callback in list(onIndexBuildComplete):
        callback(paths)
    return {"provider": "deepseek", "count": len(paths), "signature": await pathListSignature(paths)}


__all__ = [
    "applyFileSuggestion",
    "clearFileSuggestionCaches",
    "findLongestCommonPrefix",
    "generateFileSuggestions",
    "getDirectoryNames",
    "getDirectoryNamesAsync",
    "getPathsForSuggestions",
    "onIndexBuildComplete",
    "pathListSignature",
    "startBackgroundCacheRefresh",
]
