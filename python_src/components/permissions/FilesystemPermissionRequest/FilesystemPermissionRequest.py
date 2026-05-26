from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def FilesystemPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    action = str(kwargs.pop("action", "access the filesystem"))
    return permission_request(
        "FilesystemPermissionRequest",
        *args,
        tool_name=str(kwargs.pop("tool_name", kwargs.pop("toolName", "filesystem"))),
        action=action,
        kind="filesystem",
        **kwargs,
    )


__all__ = ["FilesystemPermissionRequest"]
