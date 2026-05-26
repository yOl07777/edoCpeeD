from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def NotebookEditPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request(
        "NotebookEditPermissionRequest",
        *args,
        tool_name="notebook_edit",
        action="edit a notebook",
        kind="file",
        **kwargs,
    )


__all__ = ["NotebookEditPermissionRequest"]
