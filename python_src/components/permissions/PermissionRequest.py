from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def PermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return permission_request("PermissionRequest", *args, **kwargs)


__all__ = ["PermissionRequest"]
