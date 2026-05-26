from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def SkillPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "SkillPermissionRequest",
        *args,
        tool_name="skill",
        action="load a skill",
        **kwargs,
    )
    request["skill"] = kwargs.get("skill") or kwargs.get("skillName") or kwargs.get("name")
    return request


__all__ = ["SkillPermissionRequest"]
