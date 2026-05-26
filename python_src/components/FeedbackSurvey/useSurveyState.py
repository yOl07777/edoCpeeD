from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import normalize_rating, survey_payload


async def useSurveyState(*args: Any, **kwargs: Any) -> Any:
    rating = normalize_rating(kwargs.get("rating") or (args[0] if args else None))
    submitted = bool(kwargs.get("submitted", False))
    return survey_payload("survey_state", rating=rating, comment=str(kwargs.get("comment") or ""), submitted=submitted, complete=submitted and rating is not None)


__all__ = ["useSurveyState"]
