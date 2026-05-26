from __future__ import annotations

from typing import Any

from python_src.components.permissions.FilePermissionDialog.FilePermissionDialog import FilePermissionDialog


async def useFilePermissionDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    dialog = await FilePermissionDialog(*args, **kwargs)
    return {
        "type": "file_permission_dialog_state",
        "provider": "deepseek",
        "dialog": dialog,
        "open": bool(kwargs.get("open", True)),
    }


__all__ = ["useFilePermissionDialog"]
