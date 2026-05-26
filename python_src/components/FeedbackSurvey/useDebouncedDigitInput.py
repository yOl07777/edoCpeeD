from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import normalize_rating, survey_payload


async def useDebouncedDigitInput(*args: Any, **kwargs: Any) -> Any:
    value = kwargs.get("value") or (args[0] if args else None)
    delay_ms = int(kwargs.get("delayMs", kwargs.get("delay_ms", 250)) or 250)
    rating = normalize_rating(value)
    return survey_payload("debounced_digit_input", value=value, rating=rating, valid=rating is not None, delayMs=delay_ms)


__all__ = ["useDebouncedDigitInput"]
