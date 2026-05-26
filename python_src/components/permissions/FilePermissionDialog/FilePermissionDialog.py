from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import format_permission_explanation, permission_request


async def FilePermissionDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "FilePermissionDialog",
        *args,
        tool_name=str(kwargs.pop("tool_name", kwargs.pop("toolName", "file"))),
        action=str(kwargs.pop("action", "access a file")),
        kind="file",
        **kwargs,
    )
    request["dialog"] = {
        "title": request["title"],
        "body": format_permission_explanation(request),
        "options": request["options"],
    }
    return request


__all__ = ["FilePermissionDialog"]
