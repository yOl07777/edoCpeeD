from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import normalize_rules


async def AddPermissionRules(*args: Any, **kwargs: Any) -> dict[str, Any]:
    rules = normalize_rules(kwargs.get("rules") or (args[0] if args else []))
    destination = kwargs.get("destination") or kwargs.get("scope") or "project"
    return {
        "type": "add_permission_rules",
        "provider": "deepseek",
        "destination": destination,
        "rules": rules,
        "count": len(rules),
    }


async def optionForPermissionSaveDestination(*args: Any, **kwargs: Any) -> dict[str, Any]:
    destination = str(kwargs.get("destination") or kwargs.get("scope") or (args[0] if args else "project"))
    labels = {"project": "Project settings", "user": "User settings", "local": "Local session"}
    return {"id": destination, "label": labels.get(destination, destination), "destination": destination}


__all__ = ["AddPermissionRules", "optionForPermissionSaveDestination"]
