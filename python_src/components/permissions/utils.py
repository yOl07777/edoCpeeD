from __future__ import annotations

from typing import Any

from python_src.hooks.toolPermission.permissionLogging import logPermissionDecision


async def logUnaryPermissionEvent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    event = {
        "type": "permission_event",
        "provider": "deepseek",
        "name": str(kwargs.get("name") or kwargs.get("event") or (args[0] if args else "permission")),
        "metadata": kwargs.get("metadata") or {},
    }
    logPermissionDecision({"source": "components.permissions.utils", **event}, {"behavior": "log"})
    return event


__all__ = ["logUnaryPermissionEvent"]
