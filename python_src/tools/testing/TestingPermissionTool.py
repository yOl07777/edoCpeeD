"""Testing-only permission tool shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema


async def testing_permission(action: str = "allow", *, reason: str = "") -> dict[str, Any]:
    allowed = action.lower() not in {"deny", "reject", "block"}
    return {"allowed": allowed, "action": action, "reason": reason}


TestingPermissionTool = PythonTool(
    name="testing_permission",
    description="Return a deterministic permission decision for tests.",
    parameters=object_schema(
        {
            "action": {"type": "string", "default": "allow"},
            "reason": {"type": "string", "default": ""},
        }
    ),
    handler=testing_permission,
    read_only=True,
)

__all__ = ["TestingPermissionTool", "testing_permission"]
