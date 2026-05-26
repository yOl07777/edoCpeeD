from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def survey_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_rating(value: Any = None) -> int | None:
    if value in {None, ""}:
        return None
    try:
        rating = int(str(value).strip())
    except ValueError:
        return None
    if 1 <= rating <= 5:
        return rating
    return None


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

