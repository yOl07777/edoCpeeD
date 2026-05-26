from __future__ import annotations

from typing import Any

from python_src.hooks.useDiffData import useDiffData


async def computeEditsFromContents(old: Any = "", new: Any = "", *_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    data = await useDiffData(old, new, **kwargs)
    return [{"type": "replace", "old": str(old), "new": str(new), "diff": data["diff"]}] if data["diff"] else []


async def useDiffInIDE(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    edits = await computeEditsFromContents(kwargs.get("old", ""), kwargs.get("new", ""))
    return {
        "provider": "deepseek",
        "path": str(kwargs.get("path", "")),
        "ide": str(kwargs.get("ide", "default")),
        "edits": edits,
        "openCommand": None,
        "dryRun": True,
    }


__all__ = ["computeEditsFromContents", "useDiffInIDE"]
