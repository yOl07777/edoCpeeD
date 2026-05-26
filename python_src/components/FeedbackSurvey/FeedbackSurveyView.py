from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import normalize_rating, survey_payload


def isValidResponseInput(value: Any) -> bool:
    return normalize_rating(value) is not None


async def FeedbackSurveyView(*args: Any, **kwargs: Any) -> Any:
    rating = normalize_rating(kwargs.get("rating") or (args[0] if args else None))
    comment = str(kwargs.get("comment") or "")
    return survey_payload(
        "feedback_survey_view",
        prompt="Rate this DeepSeek Code session from 1 to 5.",
        rating=rating,
        comment=comment,
        valid=rating is not None,
        submitted=bool(kwargs.get("submitted", False)),
    )


__all__ = ["FeedbackSurveyView", "isValidResponseInput"]
