from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import format_permission_explanation, permission_request


async def PermissionDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("PermissionDialog", *args, **kwargs)
    request["dialog"] = {
        "title": request["title"],
        "body": format_permission_explanation(request),
        "options": request["options"],
    }
    return request


__all__ = ["PermissionDialog"]
