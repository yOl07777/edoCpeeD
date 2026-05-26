from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def BashPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "BashPermissionRequest",
        *args,
        tool_name="run_shell",
        action="run a shell command",
        kind="shell",
        **kwargs,
    )
    request["command"] = kwargs.get("command") or kwargs.get("cmd")
    return request


__all__ = ["BashPermissionRequest"]
