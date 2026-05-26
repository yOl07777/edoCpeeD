"""Implementation for `/add-dir`."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

_spec = importlib.util.spec_from_file_location("_add_dir_validation", Path(__file__).with_name("validation.py"))
_validation = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_validation)
addDirHelpMessage = _validation.addDirHelpMessage
validateDirectoryForWorkspace = _validation.validateDirectoryForWorkspace


async def call(
    onDone: Callable[..., Any] | None = None,
    context: dict[str, Any] | None = None,
    args: str | None = None,
    *,
    remember: bool = False,
) -> dict[str, Any]:
    directory_path = (args or "").strip()
    if not directory_path:
        result = {"resultType": "emptyPath"}
        message = addDirHelpMessage(result)
        if onDone:
            onDone(message)
        return {"ok": False, "message": message, "result": result}

    app_state = context.get("appState", context) if isinstance(context, dict) else {}
    permission_context = app_state.get("toolPermissionContext") if isinstance(app_state, dict) else {}
    result = await validateDirectoryForWorkspace(directory_path, permission_context)
    if result.get("resultType") != "success":
        message = addDirHelpMessage(result)
        if onDone:
            onDone(message)
        return {"ok": False, "message": message, "result": result}

    path = str(result["absolutePath"])
    dirs = permission_context.setdefault("workingDirectories", []) if isinstance(permission_context, dict) else []
    if path not in dirs:
        dirs.append(path)
    message = f"Added {path} as a working directory"
    if remember:
        message += " and saved to local settings"
    else:
        message += " for this session"
    if onDone:
        onDone(message)
    return {"ok": True, "message": message, "path": path, "remember": remember}
