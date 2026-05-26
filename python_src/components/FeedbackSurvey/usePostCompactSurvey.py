from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import survey_payload


async def usePostCompactSurvey(*args: Any, **kwargs: Any) -> Any:
    compacted = bool(kwargs.get("compacted", args[0] if args else False))
    return survey_payload(
        "post_compact_survey_hook",
        shouldShow=compacted and bool(kwargs.get("enabled", True)),
        prompt="Did context compaction preserve what mattered?",
    )


__all__ = ["usePostCompactSurvey"]
