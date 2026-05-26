from __future__ import annotations

from python_src.components.StructuredDiff.Fallback import (
    StructuredDiffFallback,
    calculateWordDiffs,
    numberDiffLines,
    processAdjacentLines,
    transformLinesToObjects,
)


async def StructuredDiff(diff: str = "", *_args, **kwargs):
    rendered = await StructuredDiffFallback(diff, **kwargs)
    rendered["type"] = "structured_diff"
    rendered["additions"] = sum(1 for line in rendered["diff"].splitlines() if line.startswith("+") and not line.startswith("+++"))
    rendered["removals"] = sum(1 for line in rendered["diff"].splitlines() if line.startswith("-") and not line.startswith("---"))
    return rendered


__all__ = [
    "StructuredDiff",
    "StructuredDiffFallback",
    "calculateWordDiffs",
    "numberDiffLines",
    "processAdjacentLines",
    "transformLinesToObjects",
]
