from __future__ import annotations

import os
from typing import Any

from python_src.utils.permissions.PermissionRule import PermissionRule
from python_src.utils.permissions.permissionRuleParser import permissionRuleValueFromString
from python_src.utils.permissions.permissions import checkRuleBasedPermissions
from python_src.utils.permissions.permissionsLoader import (
    addPermissionRulesToSettings,
    deletePermissionRuleFromSettings,
    loadAllPermissionRulesFromDisk,
)


async def permissions_command(
    action: str = "list",
    *,
    rule: str | dict[str, Any] | None = None,
    tool: str | None = None,
    value: str = "*",
    behavior: str = "ask",
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    if action == "list":
        rules = await loadAllPermissionRulesFromDisk(cwd)
        return {"rules": rules, "count": len(rules)}
    if action == "check":
        return await checkRuleBasedPermissions(tool or "*", value, cwd=cwd)
    if action == "add":
        parsed = await permissionRuleValueFromString(rule) if isinstance(rule, str) else PermissionRule(
            tool=tool or str((rule or {}).get("tool", "*")),
            value=value if rule is None else str((rule or {}).get("value", value)),
            behavior=behavior if rule is None else str((rule or {}).get("behavior", behavior)),  # type: ignore[arg-type]
            source=str((rule or {}).get("source", "project")) if isinstance(rule, dict) else "project",
        )
        rules = await addPermissionRulesToSettings([parsed], cwd=cwd)
        return {"rule": parsed.to_dict(), "rules": rules}
    if action == "delete":
        parsed = await permissionRuleValueFromString(rule) if isinstance(rule, str) else {
            "tool": tool or str((rule or {}).get("tool", "*")),
            "value": value if rule is None else str((rule or {}).get("value", value)),
            "behavior": behavior if rule is None else str((rule or {}).get("behavior", behavior)),
            "source": str((rule or {}).get("source", "project")) if isinstance(rule, dict) else "project",
        }
        deleted = await deletePermissionRuleFromSettings(parsed, cwd=cwd)
        return {"deleted": deleted}
    raise ValueError(f"Unsupported permissions action: {action}")


call = permissions_command
