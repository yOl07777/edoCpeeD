from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def FallbackPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("FallbackPermissionRequest", *args, **kwargs)
    request["fallback"] = True
    request["message"] = "No specialized permission UI is available; using structured fallback."
    return request


__all__ = ["FallbackPermissionRequest"]
