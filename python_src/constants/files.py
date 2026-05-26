from __future__ import annotations

from pathlib import Path
from typing import Any


BINARY_EXTENSIONS = {
    ".7z",
    ".a",
    ".avi",
    ".bin",
    ".bmp",
    ".class",
    ".dll",
    ".dmg",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".o",
    ".pdf",
    ".png",
    ".pyc",
    ".rar",
    ".so",
    ".tar",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}


async def hasBinaryExtension(path: Any = "", *_args: Any, **_kwargs: Any) -> bool:
    return Path(str(path or "")).suffix.lower() in BINARY_EXTENSIONS


async def isBinaryContent(content: Any = b"", *_args: Any, **_kwargs: Any) -> bool:
    if isinstance(content, str):
        sample = content[:4096].encode("utf-8", errors="ignore")
    else:
        sample = bytes(content or b"")[:4096]
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    text_controls = sum(1 for byte in sample if byte < 32 and byte not in {9, 10, 13})
    return text_controls / max(len(sample), 1) > 0.3


__all__ = ["BINARY_EXTENSIONS", "hasBinaryExtension", "isBinaryContent"]
