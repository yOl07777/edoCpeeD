"""Prompt dump helpers for local DeepSeek request debugging."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

_REQUEST_CACHE: list[dict[str, Any]] = []
_DUMP_ENABLED = False
_DUMP_PATH: Path | None = None


async def getDumpPromptsPath(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path).expanduser().resolve()
    env_path = os.getenv("DEEPSEEK_DUMP_PROMPTS_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return (Path.cwd() / ".deepseek_prompt_dumps.jsonl").resolve()


async def addApiRequestToCache(request: dict[str, Any], max_entries: int = 20) -> dict[str, Any]:
    entry = {"timestamp": time.time(), "request": request}
    _REQUEST_CACHE.append(entry)
    del _REQUEST_CACHE[:-max_entries]
    if _DUMP_ENABLED:
        path = _DUMP_PATH or await getDumpPromptsPath()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    return entry


async def getLastApiRequests(limit: int = 20) -> list[dict[str, Any]]:
    return list(_REQUEST_CACHE[-int(limit) :])


async def clearApiRequestCache() -> None:
    _REQUEST_CACHE.clear()


async def clearDumpState() -> None:
    global _DUMP_ENABLED, _DUMP_PATH
    _DUMP_ENABLED = False
    _DUMP_PATH = None


async def clearAllDumpState() -> None:
    await clearApiRequestCache()
    await clearDumpState()


async def createDumpPromptsFetch(fetch: Callable[..., Any], path: str | Path | None = None) -> Callable[..., Any]:
    """Wrap an async/sync fetch callable and dump request arguments."""

    global _DUMP_ENABLED, _DUMP_PATH
    _DUMP_ENABLED = True
    _DUMP_PATH = await getDumpPromptsPath(path)

    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        await addApiRequestToCache({"args": args, "kwargs": kwargs})
        result = fetch(*args, **kwargs)
        if hasattr(result, "__await__"):
            return await result
        return result

    return wrapped

