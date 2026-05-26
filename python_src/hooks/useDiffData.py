from __future__ import annotations

import difflib
from typing import Any


async def useDiffData(old: Any = "", new: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    old_text = str(kwargs.get("old", kwargs.get("old_text", old)) or "")
    new_text = str(kwargs.get("new", kwargs.get("new_text", new)) or "")
    diff = "\n".join(
        difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile=str(kwargs.get("fromfile", "before")),
            tofile=str(kwargs.get("tofile", "after")),
            lineterm="",
        )
    )
    lines = diff.splitlines()
    return {
        "provider": "deepseek",
        "diff": diff,
        "lines": lines,
        "additions": sum(1 for line in lines if line.startswith("+") and not line.startswith("+++")),
        "removals": sum(1 for line in lines if line.startswith("-") and not line.startswith("---")),
    }


__all__ = ["useDiffData"]
