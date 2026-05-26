from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import permission_request


async def ComputerUseApproval(*args: Any, **kwargs: Any) -> dict[str, Any]:
    request = permission_request(
        "ComputerUseApproval",
        *args,
        tool_name="computer_use",
        action="control the computer",
        **kwargs,
    )
    request["requiresExplicitApproval"] = True
    return request


__all__ = ["ComputerUseApproval"]
