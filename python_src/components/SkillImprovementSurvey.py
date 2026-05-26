from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def SkillImprovementSurvey(*args: Any, **kwargs: Any) -> Any:
    skill = str(option(args, kwargs, "skill", scalar_arg(args, "skill")))
    rating = option(args, kwargs, "rating", None)
    return component_payload("skill_improvement_survey", skill=skill, rating=rating, submitted=rating is not None)


__all__ = ["SkillImprovementSurvey"]
