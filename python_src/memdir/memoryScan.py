"""Memory-directory scanning primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from python_src.utils.frontmatterParser import parseFrontmatter

from .memoryTypes import MemoryType, parseMemoryType

MAX_MEMORY_FILES = 200
FRONTMATTER_MAX_LINES = 30


@dataclass(frozen=True)
class MemoryHeader:
    filename: str
    filePath: str
    mtimeMs: float
    description: str | None = None
    type: MemoryType | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "filePath": self.filePath,
            "mtimeMs": self.mtimeMs,
            "description": self.description,
            "type": self.type,
        }


def _read_frontmatter_window(path: Path) -> str:
    lines: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if index >= FRONTMATTER_MAX_LINES:
                break
            lines.append(line)
    return "".join(lines)


async def scanMemoryFiles(memoryDir: str | Path, *_args: Any, **_kwargs: Any) -> list[MemoryHeader]:
    """Scan a memory directory for markdown files and return newest headers."""

    root = Path(memoryDir)
    if not root.is_dir():
        return []
    memories: list[MemoryHeader] = []
    try:
        candidates = [path for path in root.rglob("*.md") if path.name != "MEMORY.md"]
    except OSError:
        return []

    for path in candidates:
        try:
            content = _read_frontmatter_window(path)
            parsed = parseFrontmatter(content, str(path))
            frontmatter = parsed.get("frontmatter", {}) if isinstance(parsed, dict) else {}
            if not isinstance(frontmatter, dict):
                frontmatter = {}
            stat = path.stat()
            description = frontmatter.get("description")
            memory_type = await parseMemoryType(frontmatter.get("type"))
            memories.append(
                MemoryHeader(
                    filename=path.relative_to(root).as_posix(),
                    filePath=str(path.resolve()),
                    mtimeMs=stat.st_mtime * 1000,
                    description=str(description).strip() if description else None,
                    type=memory_type,
                )
            )
        except OSError:
            continue

    memories.sort(key=lambda item: item.mtimeMs, reverse=True)
    return memories[:MAX_MEMORY_FILES]


async def formatMemoryManifest(memories: list[MemoryHeader | dict[str, Any]], *_args: Any, **_kwargs: Any) -> str:
    """Format memory headers as one manifest line per memory file."""

    lines: list[str] = []
    for memory in memories:
        if isinstance(memory, MemoryHeader):
            filename = memory.filename
            mtime_ms = memory.mtimeMs
            description = memory.description
            memory_type = memory.type
        else:
            filename = str(memory.get("filename", ""))
            mtime_ms = float(memory.get("mtimeMs", 0) or 0)
            description = memory.get("description")
            memory_type = memory.get("type")
        tag = f"[{memory_type}] " if memory_type else ""
        timestamp = datetime.fromtimestamp(mtime_ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        suffix = f": {description}" if description else ""
        lines.append(f"- {tag}{filename} ({timestamp}){suffix}")
    return "\n".join(lines)


__all__ = ["MemoryHeader", "formatMemoryManifest", "scanMemoryFiles"]
