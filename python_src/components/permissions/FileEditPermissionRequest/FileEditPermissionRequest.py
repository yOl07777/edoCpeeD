from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def FileEditPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "FileEditPermissionRequest",
        *args,
        tool_name="edit_file",
        action="edit a file",
        kind="file",
        **kwargs,
    )


__all__ = ["FileEditPermissionRequest"]
