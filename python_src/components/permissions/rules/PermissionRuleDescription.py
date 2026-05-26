from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import normalize_rule


async def PermissionRuleDescription(*args: Any, **kwargs: Any) -> dict[str, Any]:
    rule = normalize_rule(args[0] if args else None, **kwargs)
    return {
        "type": "permission_rule_description",
        "provider": "deepseek",
        "rule": rule,
        "text": f"{rule['behavior']} {rule['tool']} for {rule['value']}",
    }


__all__ = ["PermissionRuleDescription"]
