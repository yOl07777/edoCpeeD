from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def FileWritePermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "FileWritePermissionRequest",
        *args,
        tool_name="write_file",
        action="write a file",
        kind="file",
        **kwargs,
    )


__all__ = ["FileWritePermissionRequest"]
