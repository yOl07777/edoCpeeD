from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def WorkerPendingPermission(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request("WorkerPendingPermission", *args, **kwargs)
    request["pending"] = True
    request["worker"] = kwargs.get("worker") or kwargs.get("agent")
    return request


__all__ = ["WorkerPendingPermission"]
