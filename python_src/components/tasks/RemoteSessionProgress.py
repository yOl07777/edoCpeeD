from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def formatReviewStageCounts(*args: Any, **kwargs: Any) -> Any:
    counts = kwargs.get("counts") or (args[0] if args else {}) or {}
    if isinstance(counts, dict):
        return ", ".join(f"{key}: {value}" for key, value in counts.items())
    return str(counts)


async def RemoteSessionProgress(*args: Any, **kwargs: Any) -> Any:
    session = normalize_task(kwargs.get("session") or (args[0] if args else None), **kwargs)
    return task_payload("remote_session_progress", session=session, reviewCounts=await formatReviewStageCounts(kwargs.get("reviewCounts", {})))


__all__ = ["RemoteSessionProgress", "formatReviewStageCounts"]
