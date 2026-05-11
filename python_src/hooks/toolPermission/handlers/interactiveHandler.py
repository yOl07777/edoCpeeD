from __future__ import annotations

from typing import Any

from python_src.hooks.toolPermission.permissionLogging import logPermissionDecision
from python_src.utils.permissions.permissions import checkRuleBasedPermissions


async def handleInteractivePermission(context: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    tool_name = str(context.get("tool_name") or context.get("tool") or "")
    value = str(context.get("value") or context.get("input") or "*")
    decision = await checkRuleBasedPermissions(tool_name, value, rules=rules or [])
    logPermissionDecision(context, decision)
    return decision
