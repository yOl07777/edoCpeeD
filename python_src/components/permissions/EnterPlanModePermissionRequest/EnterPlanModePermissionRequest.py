from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def EnterPlanModePermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "EnterPlanModePermissionRequest",
        *args,
        tool_name="enter_plan_mode",
        action="enter plan mode",
        **kwargs,
    )


__all__ = ["EnterPlanModePermissionRequest"]
