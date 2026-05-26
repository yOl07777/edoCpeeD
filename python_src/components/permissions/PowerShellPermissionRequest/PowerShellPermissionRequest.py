from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def PowerShellPermissionRequest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "PowerShellPermissionRequest",
        *args,
        tool_name="run_powershell",
        action="run a PowerShell command",
        kind="powershell",
        **kwargs,
    )
    request["command"] = kwargs.get("command") or kwargs.get("cmd")
    return request


__all__ = ["PowerShellPermissionRequest"]
