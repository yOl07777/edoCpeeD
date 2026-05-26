from __future__ import annotations

from typing import Any

from python_src.utils.permissions.PermissionResult import getRuleBehaviorDescription


async def PermissionRuleExplanation(*args: Any, **kwargs: Any) -> dict[str, Any]:
    rule = kwargs.get("rule") or (args[0] if args else {}) or {}
    behavior = rule.get("behavior") if isinstance(rule, dict) else getattr(rule, "behavior", "ask")
    value = rule.get("value") if isinstance(rule, dict) else getattr(rule, "value", None)
    return {
        "type": "permission_rule_explanation",
        "provider": "deepseek",
        "behavior": behavior,
        "value": value,
        "description": getRuleBehaviorDescription(str(behavior)),
    }


__all__ = ["PermissionRuleExplanation"]
