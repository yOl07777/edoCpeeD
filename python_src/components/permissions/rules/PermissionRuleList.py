from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import normalize_rules


async def PermissionRuleList(*args: Any, **kwargs: Any) -> dict[str, Any]:
    rules = normalize_rules(kwargs.get("rules") or (args[0] if args else []))
    return {"type": "permission_rule_list", "provider": "deepseek", "rules": rules, "count": len(rules)}


__all__ = ["PermissionRuleList"]
