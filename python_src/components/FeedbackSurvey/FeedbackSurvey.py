from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import normalize_rating, survey_payload
from python_src.components.FeedbackSurvey.FeedbackSurveyView import FeedbackSurveyView


async def FeedbackSurvey(*args: Any, **kwargs: Any) -> Any:
    rating = normalize_rating(kwargs.get("rating") or (args[0] if args else None))
    return survey_payload(
        "feedback_survey",
        rating=rating,
        comment=str(kwargs.get("comment") or ""),
        view=await FeedbackSurveyView(rating=rating, comment=kwargs.get("comment", "")),
        enabled=bool(kwargs.get("enabled", True)),
    )


__all__ = ["FeedbackSurvey"]
