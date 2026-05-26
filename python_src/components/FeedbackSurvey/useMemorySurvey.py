from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import survey_payload


async def useMemorySurvey(*args: Any, **kwargs: Any) -> Any:
    facts_count = int(kwargs.get("factsCount", kwargs.get("facts_count", args[0] if args else 0)) or 0)
    return survey_payload(
        "memory_survey_hook",
        shouldShow=facts_count > 0 and bool(kwargs.get("enabled", True)),
        factsCount=facts_count,
        prompt="Was the saved memory useful?",
    )


__all__ = ["useMemorySurvey"]
