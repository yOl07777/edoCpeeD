from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerSkillifySkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("skillify", "Turn repeated workflows into a local SKILL.md skill.", allowedTools=["Read", "Edit"])


__all__ = ["registerSkillifySkill"]
