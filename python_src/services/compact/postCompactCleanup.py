"""Post-compaction cleanup hooks."""

from __future__ import annotations

from typing import Any

from .compactWarningState import clearCompactWarningSuppression
from .microCompact import resetMicrocompactState


_cleanup_counts: dict[str, int] = {}


def _is_main_thread(query_source: str | None) -> bool:
    return query_source is None or query_source == "sdk" or query_source.startswith("repl_main_thread")


async def runPostCompactCleanup(querySource: str | None = None, *_: Any, **__: Any) -> dict[str, Any]:
    main_thread = _is_main_thread(querySource)
    await resetMicrocompactState()
    await clearCompactWarningSuppression()
    cleared = ["microcompact_state", "compact_warning"]
    if main_thread:
        cleared.extend(["user_context_cache", "memory_files_cache"])
    cleared.extend(["system_prompt_sections", "classifier_approvals", "speculative_checks", "session_messages_cache"])
    for item in cleared:
        _cleanup_counts[item] = _cleanup_counts.get(item, 0) + 1
    return {"querySource": querySource, "mainThread": main_thread, "cleared": cleared, "counts": dict(_cleanup_counts)}


__all__ = ["runPostCompactCleanup"]
