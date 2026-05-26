from __future__ import annotations

from typing import Any

from ._basic import first_mapping, normalize_bool, pick


async def useSkillImprovementSurvey(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    used_count = int(pick(options, "usedCount", "runs", default=0))
    dismissed = normalize_bool(pick(options, "dismissed", default=False))
    visible = used_count >= int(pick(options, "threshold", default=3)) and not dismissed
    return {"provider": "deepseek", "visible": visible, "usedCount": used_count, "prompt": "How useful was this skill?" if visible else ""}
