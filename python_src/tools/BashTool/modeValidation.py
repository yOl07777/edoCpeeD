from __future__ import annotations

from typing import Any

from python_src.tools.BashTool.bashPermissions import bashToolCheckPermission
from python_src.tools.BashTool.readOnlyValidation import isCommandSafeViaFlagParsing


DEFAULT_AUTO_ALLOWED_COMMANDS = [
    "cat",
    "head",
    "tail",
    "ls",
    "pwd",
    "rg",
    "grep",
    "find",
    "git status",
    "git diff",
    "git log",
]


def getAutoAllowedCommands(extra: list[str] | None = None) -> list[str]:
    commands = list(DEFAULT_AUTO_ALLOWED_COMMANDS)
    for command in extra or []:
        if command not in commands:
            commands.append(command)
    return commands


def checkPermissionMode(
    command: str,
    *,
    mode: str = "default",
    allowed_commands: list[str] | None = None,
) -> dict[str, Any]:
    if mode in {"bypass", "dangerously_skip_permissions"}:
        return {"allowed": True, "mode": mode, "reason": None}
    if mode in {"read-only", "readonly", "plan"}:
        ok = isCommandSafeViaFlagParsing(command)
        return {"allowed": ok, "mode": mode, "reason": None if ok else "Command is not read-only."}
    allowed = bashToolCheckPermission(command, getAutoAllowedCommands(allowed_commands))
    return {"allowed": allowed, "mode": mode, "reason": None if allowed else "Command needs approval."}
