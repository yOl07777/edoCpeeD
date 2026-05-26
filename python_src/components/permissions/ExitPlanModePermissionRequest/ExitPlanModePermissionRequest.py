from __future__ import annotations

import re
from typing import Any

from python_src.components.permissions._shared import normalize_permission_input, permission_request


async def ExitPlanModePermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "ExitPlanModePermissionRequest",
        *args,
        tool_name="exit_plan_mode",
        action="leave plan mode and apply the plan",
        **kwargs,
    )


async def autoNameSessionFromPlan(*args: Any, **kwargs: Any) -> str:
    data = normalize_permission_input(*args, **kwargs)
    plan = str(data.get("plan") or data.get("content") or data.get("input") or "plan")
    words = re.findall(r"[A-Za-z0-9_]+", plan.lower())[:6]
    return "-".join(words) or "deepseek-plan"


async def buildPermissionUpdates(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    data = normalize_permission_input(*args, **kwargs)
    updates = data.get("updates") or data.get("permissions") or []
    if isinstance(updates, list):
        return [dict(item) if isinstance(item, dict) else {"value": str(item)} for item in updates]
    return [{"value": str(updates)}]


async def buildPlanApprovalOptions(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    return [
        {"id": "approve_plan", "label": "Approve plan", "behavior": "allow", "scope": "plan"},
        {"id": "revise_plan", "label": "Revise plan", "behavior": "ask", "scope": "plan"},
        {"id": "deny", "label": "Deny", "behavior": "deny", "scope": "once"},
    ]


__all__ = [
    "ExitPlanModePermissionRequest",
    "autoNameSessionFromPlan",
    "buildPermissionUpdates",
    "buildPlanApprovalOptions",
]
