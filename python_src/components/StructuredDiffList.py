from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def StructuredDiffList(*args: Any, **kwargs: Any) -> Any:
    diffs = normalize_items(option(args, kwargs, "diffs", scalar_arg(args, [])))
    return component_payload("structured_diff_list", diffs=diffs, count=len(diffs), changed=sum(1 for diff in diffs if diff.get("changed", True)))


__all__ = ["StructuredDiffList"]
