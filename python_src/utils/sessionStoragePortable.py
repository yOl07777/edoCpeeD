"""Portable session-storage helpers for the Python migration."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


LITE_READ_BUF_SIZE = 64 * 1024
MAX_SANITIZED_LENGTH = 180
SKIP_PRECOMPACT_THRESHOLD = 4 * 1024
_UUID_RE = re.compile(r"^[0-9a-fA-F]{32}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


async def canonicalizePath(path: str | os.PathLike[str]) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


async def sanitizePath(path: str | os.PathLike[str]) -> str:
    text = await canonicalizePath(path)
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip().replace(":", ""))
    sanitized = sanitized.strip("-._") or "root"
    return sanitized[:MAX_SANITIZED_LENGTH]


async def getProjectsDir() -> str:
    root = (
        os.getenv("DEEPCODE_CONFIG_HOME")
        or os.getenv("DEEPSEEK_CONFIG_DIR")
        or str(Path.home() / ".deepseek")
    )
    return str(Path(root) / "projects")


async def getProjectDir(projectDir: str | os.PathLike[str]) -> str:
    return str(Path(await getProjectsDir()) / await sanitizePath(projectDir))


async def findProjectDir(projectDir: str | os.PathLike[str]) -> str | None:
    path = Path(await getProjectDir(projectDir))
    return str(path) if path.exists() else None


async def validateUuid(value: str) -> str | None:
    return value if _UUID_RE.match(str(value)) else None


async def readHeadAndTail(filePath: str | os.PathLike[str], size: int = LITE_READ_BUF_SIZE) -> dict[str, Any] | None:
    path = Path(filePath)
    try:
        stat = path.stat()
        with path.open("rb") as handle:
            head_bytes = handle.read(size)
            if stat.st_size > size:
                handle.seek(max(0, stat.st_size - size))
            else:
                handle.seek(0)
            tail_bytes = handle.read(size)
        return {
            "head": head_bytes.decode("utf-8", errors="replace"),
            "tail": tail_bytes.decode("utf-8", errors="replace"),
            "mtime": stat.st_mtime * 1000,
            "size": stat.st_size,
            "filePath": str(path),
        }
    except OSError:
        return None


async def readSessionLite(filePath: str | os.PathLike[str]) -> dict[str, Any] | None:
    return await readHeadAndTail(filePath)


async def readTranscriptForLoad(filePath: str | os.PathLike[str], maxBytes: int | None = None) -> str:
    path = Path(filePath)
    data = path.read_bytes()
    if maxBytes and len(data) > maxBytes:
        data = data[-maxBytes:]
    return data.decode("utf-8", errors="replace")


async def resolveSessionFilePath(sessionId: str, projectDir: str | os.PathLike[str] | None = None) -> str | None:
    valid = await validateUuid(sessionId)
    if not valid:
        return None
    roots = [Path(await getProjectDir(projectDir or os.getcwd()))]
    projects = Path(await getProjectsDir())
    if projectDir is None and projects.exists():
        roots = [path for path in projects.iterdir() if path.is_dir()]
    for root in roots:
        candidate = root / f"{valid}.jsonl"
        if candidate.exists():
            return str(candidate)
    return None


async def unescapeJsonString(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return value


def _extract_field_from_lines(text: str, field: str, *, reverse: bool = False) -> str | None:
    lines = text.splitlines()
    if reverse:
        lines = list(reversed(lines))
    for line in lines:
        try:
            data = json.loads(line)
        except Exception:
            continue
        value = data.get(field)
        if isinstance(value, str):
            return value
        message = data.get("message")
        if isinstance(message, dict) and isinstance(message.get(field), str):
            return message[field]
    return None


async def extractJsonStringField(text: str, field: str) -> str | None:
    return _extract_field_from_lines(text, field)


async def extractLastJsonStringField(text: str, field: str) -> str | None:
    return _extract_field_from_lines(text, field, reverse=True)


async def extractFirstPromptFromHead(head: str) -> str | None:
    for line in head.splitlines():
        try:
            data = json.loads(line)
        except Exception:
            continue
        if data.get("type") != "user":
            continue
        message = data.get("message")
        content = message.get("content") if isinstance(message, dict) else data.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [item.get("text") for item in content if isinstance(item, dict) and isinstance(item.get("text"), str)]
            if parts:
                return "\n".join(parts)
    return None


__all__ = [
    "LITE_READ_BUF_SIZE",
    "MAX_SANITIZED_LENGTH",
    "SKIP_PRECOMPACT_THRESHOLD",
    "canonicalizePath",
    "extractFirstPromptFromHead",
    "extractJsonStringField",
    "extractLastJsonStringField",
    "findProjectDir",
    "getProjectDir",
    "getProjectsDir",
    "readHeadAndTail",
    "readSessionLite",
    "readTranscriptForLoad",
    "resolveSessionFilePath",
    "sanitizePath",
    "unescapeJsonString",
    "validateUuid",
]
