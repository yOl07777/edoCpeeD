from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import format_permission_explanation, permission_request


async def PermissionExplainerContent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("PermissionExplainerContent", *args, **kwargs)
    request["text"] = format_permission_explanation(request)
    return request


async def usePermissionExplainerUI(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("usePermissionExplainerUI", *args, **kwargs)
    return {
        "type": "permission_explainer_ui",
        "provider": "deepseek",
        "request": request,
        "text": format_permission_explanation(request),
    }


__all__ = ["PermissionExplainerContent", "usePermissionExplainerUI"]
