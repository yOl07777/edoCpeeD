from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import survey_payload
from python_src.components.FeedbackSurvey.useSurveyState import useSurveyState


async def useFeedbackSurvey(*args: Any, **kwargs: Any) -> Any:
    state = await useSurveyState(*args, **kwargs)
    return survey_payload(
        "feedback_survey_hook",
        state=state,
        shouldShow=bool(kwargs.get("enabled", True)) and not state["submitted"],
        trigger=kwargs.get("trigger", "manual"),
    )


__all__ = ["useFeedbackSurvey"]
