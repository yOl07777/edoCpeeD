from __future__ import annotations

from typing import Any

from python_src.components.permissions.rules._shared import workspace_entry


async def RemoveWorkspaceDirectory(*args: Any, **kwargs: Any) -> dict[str, Any]:
    path = kwargs.get("path") or (args[0] if args else ".")
    entry = workspace_entry(path)
    entry.update({"type": "remove_workspace_directory", "provider": "deepseek", "allowed": False})
    return entry


__all__ = ["RemoveWorkspaceDirectory"]
