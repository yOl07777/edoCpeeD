from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import format_permission_explanation, permission_request


async def PermissionPrompt(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("PermissionPrompt", *args, **kwargs)
    request["prompt"] = format_permission_explanation(request)
    return request


__all__ = ["PermissionPrompt"]
