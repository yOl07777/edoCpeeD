from __future__ import annotations

from typing import Any

from python_src.components.diff._shared import diff_payload, normalize_file, summarize_diff
from python_src.components.StructuredDiff.Fallback import StructuredDiffFallback


async def DiffDetailView(*args: Any, **kwargs: Any) -> Any:
    file_info = normalize_file(kwargs.get("file") or (args[0] if args else {"path": kwargs.get("path", "diff"), "diff": kwargs.get("diff", "")}))
    diff = kwargs.get("diff") or file_info.get("diff") or ""
    structured = await StructuredDiffFallback(diff, old_text=kwargs.get("old_text"), new_text=kwargs.get("new_text"))
    return diff_payload("diff_detail_view", file=file_info, summary=summarize_diff(structured["diff"]), structured=structured)


__all__ = ["DiffDetailView"]
