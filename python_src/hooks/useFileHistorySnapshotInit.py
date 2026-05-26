from __future__ import annotations

from pathlib import Path
from typing import Any


async def useFileHistorySnapshotInit(files: list[Any] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    root = Path(str(kwargs.get("cwd", Path.cwd())))
    snapshots: dict[str, str] = {}
    for item in list(kwargs.get("files", files or [])):
        path = Path(str(item))
        if not path.is_absolute():
            path = root / path
        try:
            snapshots[str(path)] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            snapshots[str(path)] = ""
    return {"provider": "deepseek", "snapshots": snapshots, "count": len(snapshots)}


__all__ = ["useFileHistorySnapshotInit"]
