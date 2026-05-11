from __future__ import annotations

import re
from typing import Any

from python_src.tools.PowerShellTool.powershellPermissions import powershellToolCheckPermission
from python_src.tools.PowerShellTool.readOnlyValidation import isReadOnlyCommand


AUTO_ALLOWED_COMMANDS = [
    "Get-ChildItem",
    "Get-Content",
    "Get-Location",
    "Get-Process",
    "Get-Service",
    "Select-String",
    "git status",
    "git diff",
    "git log",
]


def isSymlinkCreatingCommand(command: str) -> bool:
    return bool(re.search(r"\b(New-Item|ni)\b[^\n;]*\b(SymbolicLink|Junction|HardLink)\b", command, re.IGNORECASE))


def checkPermissionMode(
    command: str,
    *,
    mode: str = "default",
    allowed_commands: list[str] | None = None,
) -> dict[str, Any]:
    if mode in {"bypass", "dangerously_skip_permissions"}:
        return {"allowed": True, "mode": mode, "reason": None}
    if isSymlinkCreatingCommand(command):
        return {"allowed": False, "mode": mode, "reason": "Symlink creation requires explicit approval."}
    if mode in {"read-only", "readonly", "plan"}:
        ok = isReadOnlyCommand(command)
        return {"allowed": ok, "mode": mode, "reason": None if ok else "Command is not read-only."}
    allowed = powershellToolCheckPermission(command, list(AUTO_ALLOWED_COMMANDS) + list(allowed_commands or []))
    return {"allowed": allowed, "mode": mode, "reason": None if allowed else "Command needs approval."}
