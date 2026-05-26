from __future__ import annotations

from typing import Any


async def useCanUseTool(tool: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    name = str(kwargs.get("tool", tool) or "")
    allowed = kwargs.get("allowedTools")
    denied = {str(item) for item in kwargs.get("deniedTools", []) or []}
    if allowed is None:
        permitted = name not in denied
    else:
        permitted = name in {str(item) for item in allowed}
    return {"provider": "deepseek", "tool": name, "canUse": permitted, "reason": "" if permitted else "tool not allowed"}


_module_migration_placeholder = useCanUseTool


__all__ = ["useCanUseTool"]
