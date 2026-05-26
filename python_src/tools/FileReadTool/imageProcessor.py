"""Local image metadata helpers for FileReadTool."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Callable

from python_src.tools.path_utils import resolve_workspace_path


def _image_size(data: bytes) -> tuple[int | None, int | None]:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")
    if data.startswith(b"\xff\xd8"):
        idx = 2
        while idx + 9 < len(data):
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            block_len = int.from_bytes(data[idx + 2 : idx + 4], "big")
            if marker in {0xC0, 0xC2} and idx + 8 < len(data):
                return int.from_bytes(data[idx + 7 : idx + 9], "big"), int.from_bytes(data[idx + 5 : idx + 7], "big")
            idx += 2 + max(block_len, 1)
    return None, None


def _describe_image(path: str | Path, *, cwd: str | None = None, inline: bool = False, max_bytes: int = 1_000_000) -> dict[str, Any]:
    target = resolve_workspace_path(str(path), cwd=cwd)
    if not target.is_file():
        raise FileNotFoundError(str(target))
    data = target.read_bytes()
    mime_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    width, height = _image_size(data[:65536])
    result: dict[str, Any] = {
        "path": str(target),
        "mimeType": mime_type,
        "bytes": len(data),
        "width": width,
        "height": height,
        "inline": False,
    }
    if inline and len(data) <= max_bytes:
        result["inline"] = True
        result["dataUri"] = f"data:{mime_type};base64,{base64.b64encode(data).decode('ascii')}"
    return result


async def getImageCreator(*args: Any, **kwargs: Any) -> Callable[..., dict[str, Any]]:
    defaults = dict(kwargs)

    def create(path: str | Path, **options: Any) -> dict[str, Any]:
        return _describe_image(path, **{**defaults, **options})

    return create


async def getImageProcessor(*args: Any, **kwargs: Any) -> Callable[..., dict[str, Any]]:
    return await getImageCreator(*args, **kwargs)


__all__ = ["getImageCreator", "getImageProcessor"]
