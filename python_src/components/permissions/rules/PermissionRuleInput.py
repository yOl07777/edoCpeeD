from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import normalize_rule


async def PermissionRuleInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    rule = normalize_rule(args[0] if args else None, **kwargs)
    return {"type": "permission_rule_input", "provider": "deepseek", "rule": rule}


__all__ = ["PermissionRuleInput"]
