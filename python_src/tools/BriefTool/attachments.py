"""Attachment helpers for the migrated BriefTool."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _workspace_root(kwargs: dict[str, Any]) -> Path:
    return Path(kwargs.get("cwd") or os.getcwd()).resolve()


def _normalize_paths(args: tuple[Any, ...], kwargs: dict[str, Any]) -> list[str]:
    value = kwargs.get("paths") or kwargs.get("attachments") or (args[0] if args else [])
    if isinstance(value, (str, os.PathLike)):
        return [str(value)]
    return [str(item) for item in (value or [])]


async def validateAttachmentPaths(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Validate local attachment paths without uploading anything."""

    root = _workspace_root(kwargs)
    valid: list[dict[str, Any]] = []
    missing: list[str] = []
    outside: list[str] = []
    for raw in _normalize_paths(args, kwargs):
        path = Path(raw).expanduser()
        resolved = (path if path.is_absolute() else root / path).resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError:
            outside.append(raw)
            continue
        if not resolved.is_file():
            missing.append(raw)
            continue
        valid.append(
            {
                "path": str(resolved),
                "relativePath": str(resolved.relative_to(root)).replace("\\", "/"),
                "bytes": resolved.stat().st_size,
            }
        )
    return {"ok": not missing and not outside, "attachments": valid, "missing": missing, "outsideWorkspace": outside}


async def resolveAttachments(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    """Return normalized attachment metadata for existing workspace files."""

    result = await validateAttachmentPaths(*args, **kwargs)
    return result["attachments"]


__all__ = ["resolveAttachments", "validateAttachmentPaths"]
