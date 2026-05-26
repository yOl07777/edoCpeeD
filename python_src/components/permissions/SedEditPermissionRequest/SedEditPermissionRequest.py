from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def SedEditPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "SedEditPermissionRequest",
        *args,
        tool_name="sed_edit",
        action="edit a file with sed",
        kind="file",
        **kwargs,
    )


__all__ = ["SedEditPermissionRequest"]
