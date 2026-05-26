from __future__ import annotations

import difflib
from typing import Any


async def transformLinesToObjects(lines: list[str] | str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    if isinstance(lines, str):
        lines = lines.splitlines()
    objects: list[dict[str, Any]] = []
    old_line = 0
    new_line = 0
    for line in lines:
        kind = "context"
        if line.startswith("+") and not line.startswith("+++"):
            kind = "add"
            new_line += 1
            number = new_line
        elif line.startswith("-") and not line.startswith("---"):
            kind = "remove"
            old_line += 1
            number = old_line
        else:
            if not line.startswith("@@") and not line.startswith("---") and not line.startswith("+++"):
                old_line += 1
                new_line += 1
            number = new_line or old_line
        objects.append({"type": kind, "line": line, "number": number})
    return objects


async def numberDiffLines(lines: list[str] | str, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    return await transformLinesToObjects(lines)


async def calculateWordDiffs(old_text: str = "", new_text: str = "", *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    diff = list(difflib.ndiff(str(old_text).split(), str(new_text).split()))
    return [{"op": item[:2].strip() or "=", "text": item[2:]} for item in diff if not item.startswith("? ")]


async def processAdjacentLines(lines: list[str] | str, *_args: Any, **_kwargs: Any) -> list[str]:
    if isinstance(lines, str):
        return lines.splitlines()
    return list(lines or [])


async def StructuredDiffFallback(diff: str = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    if not diff and ("old_text" in kwargs or "new_text" in kwargs):
        diff = "\n".join(
            difflib.unified_diff(
                str(kwargs.get("old_text") or "").splitlines(),
                str(kwargs.get("new_text") or "").splitlines(),
                fromfile=kwargs.get("fromfile", "before"),
                tofile=kwargs.get("tofile", "after"),
                lineterm="",
            )
        )
    lines = diff.splitlines()
    return {
        "type": "structured_diff_fallback",
        "provider": "deepseek",
        "diff": diff,
        "lines": await transformLinesToObjects(lines),
    }


__all__ = [
    "StructuredDiffFallback",
    "calculateWordDiffs",
    "numberDiffLines",
    "processAdjacentLines",
    "transformLinesToObjects",
]
