from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def SandboxPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "SandboxPermissionRequest",
        *args,
        tool_name=str(kwargs.pop("tool_name", kwargs.pop("toolName", "sandbox"))),
        action=str(kwargs.pop("action", "run outside the default sandbox")),
        kind="filesystem",
        **kwargs,
    )
    request["sandbox"] = {
        "requiresEscalation": bool(kwargs.get("requiresEscalation", kwargs.get("requires_escalation", True))),
        "reason": kwargs.get("reason") or kwargs.get("justification") or "",
    }
    return request


__all__ = ["SandboxPermissionRequest"]
