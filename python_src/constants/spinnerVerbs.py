from __future__ import annotations

from typing import Any


SPINNER_VERBS = [
    "Thinking",
    "Reading",
    "Writing",
    "Editing",
    "Searching",
    "Running",
    "Checking",
    "Reviewing",
]


async def getSpinnerVerbs(*_args: Any, **kwargs: Any) -> list[str]:
    extra = kwargs.get("extra") or []
    return list(dict.fromkeys([*SPINNER_VERBS, *[str(item) for item in extra]]))


__all__ = ["SPINNER_VERBS", "getSpinnerVerbs"]
