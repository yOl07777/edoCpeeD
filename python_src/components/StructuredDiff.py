from __future__ import annotations

import difflib
from typing import Any

from python_src.components._shared import component_payload, option


async def StructuredDiff(*args: Any, **kwargs: Any) -> Any:
    diff = str(option(args, kwargs, "diff", args[0] if args else ""))
    if not diff and ("old_text" in kwargs or "new_text" in kwargs):
        diff = "\n".join(
            difflib.unified_diff(
                str(kwargs.get("old_text") or "").splitlines(),
                str(kwargs.get("new_text") or "").splitlines(),
                fromfile=str(kwargs.get("fromfile", "before")),
                tofile=str(kwargs.get("tofile", "after")),
                lineterm="",
            )
        )
    lines = diff.splitlines()
    additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    removals = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    return component_payload("structured_diff", diff=diff, lines=lines, additions=additions, removals=removals, changed=bool(additions or removals))


__all__ = ["StructuredDiff"]
