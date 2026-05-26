from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def WebFetchPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "WebFetchPermissionRequest",
        *args,
        tool_name="web_fetch",
        action="fetch a web URL",
        kind="default",
        **kwargs,
    )
    request["url"] = kwargs.get("url") or kwargs.get("input_url")
    return request


__all__ = ["WebFetchPermissionRequest"]
