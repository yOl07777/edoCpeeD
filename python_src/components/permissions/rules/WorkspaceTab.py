from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import workspace_entry


async def WorkspaceTab(*args: Any, **kwargs: Any) -> dict[str, Any]:
    raw = kwargs.get("directories") or kwargs.get("paths") or (args[0] if args else []) or []
    if isinstance(raw, (str, bytes)):
        raw = [raw]
    directories = [workspace_entry(path) for path in raw]
    return {"type": "workspace_tab", "provider": "deepseek", "directories": directories, "count": len(directories)}


__all__ = ["WorkspaceTab"]
