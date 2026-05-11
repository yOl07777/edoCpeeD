from __future__ import annotations

from pathlib import Path
from typing import Any

from python_src.tools.path_utils import resolve_workspace_path


ENTRYPOINT_NAME = "MEMORY.md"
MAX_ENTRYPOINT_BYTES = 64_000
MAX_ENTRYPOINT_LINES = 1_000
DIR_EXISTS_GUIDANCE = "A memory directory exists for this project."
DIRS_EXIST_GUIDANCE = "Memory directories exist for this project."


def ensureMemoryDirExists(path: str = ".deepseek_memory", *, cwd: str | None = None) -> Path:
    target = resolve_workspace_path(path, cwd=cwd)
    target.mkdir(parents=True, exist_ok=True)
    entrypoint = target / ENTRYPOINT_NAME
    if not entrypoint.exists():
        entrypoint.write_text("# Project Memory\n", encoding="utf-8")
    return target


def truncateEntrypointContent(content: str) -> str:
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_ENTRYPOINT_BYTES:
        content = encoded[:MAX_ENTRYPOINT_BYTES].decode("utf-8", errors="ignore")
    lines = content.splitlines()
    if len(lines) > MAX_ENTRYPOINT_LINES:
        content = "\n".join(lines[:MAX_ENTRYPOINT_LINES])
    return content


def buildMemoryLines(path: str = ".deepseek_memory", *, cwd: str | None = None) -> list[str]:
    directory = ensureMemoryDirExists(path, cwd=cwd)
    entrypoint = directory / ENTRYPOINT_NAME
    content = truncateEntrypointContent(entrypoint.read_text(encoding="utf-8", errors="replace"))
    return content.splitlines()


def buildMemoryPrompt(path: str = ".deepseek_memory", *, cwd: str | None = None) -> str:
    lines = buildMemoryLines(path, cwd=cwd)
    return "\n".join(["<project_memory>", *lines, "</project_memory>"])


def buildSearchingPastContextSection(*args: Any, **kwargs: Any) -> str:
    return "Use local project memory when it is relevant to the current task."


def loadMemoryPrompt(path: str = ".deepseek_memory", *, cwd: str | None = None) -> str:
    return buildMemoryPrompt(path, cwd=cwd)
