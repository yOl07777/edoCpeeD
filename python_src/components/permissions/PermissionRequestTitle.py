from __future__ import annotations

from typing import Any

from python_src.components.permissions._shared import normalize_permission_input, permission_title


async def PermissionRequestTitle(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = normalize_permission_input(*args, **kwargs)
    tool_name = str(data.get("toolName") or data.get("tool_name") or data.get("tool") or "tool")
    action = data.get("action")
    return {
        "type": "permission_request_title",
        "provider": "deepseek",
        "toolName": tool_name,
        "title": permission_title(tool_name, str(action) if action else None),
    }


__all__ = ["PermissionRequestTitle"]
