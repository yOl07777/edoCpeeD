from __future__ import annotations

from typing import Any

from python_src.hooks.toolPermission.permissionLogging import getPermissionLog, logPermissionDecision


async def usePermissionRequestLogging(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = kwargs.get("request") or (args[0] if args else {}) or {}
    decision = kwargs.get("decision") or {"behavior": "pending"}
    logPermissionDecision(request if isinstance(request, dict) else {"request": str(request)}, decision)
    return {
        "type": "permission_request_logging",
        "provider": "deepseek",
        "logged": True,
        "logSize": len(getPermissionLog()),
    }


__all__ = ["usePermissionRequestLogging"]
