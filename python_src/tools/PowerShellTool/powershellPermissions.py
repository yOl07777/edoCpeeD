from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any

from python_src.tools.PowerShellTool.destructiveCommandWarning import getDestructiveCommandWarning
from python_src.tools.PowerShellTool.readOnlyValidation import isReadOnlyCommand


@dataclass(frozen=True)
class PowerShellPermissionRule:
    pattern: str
    read_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"pattern": self.pattern, "read_only": self.read_only}


def powershellPermissionRule(pattern: str, read_only: bool = False) -> PowerShellPermissionRule:
    return PowerShellPermissionRule(pattern=pattern, read_only=read_only)


def _pattern(rule: str | dict[str, Any] | PowerShellPermissionRule) -> str:
    if isinstance(rule, PowerShellPermissionRule):
        return rule.pattern
    if isinstance(rule, dict):
        return str(rule.get("pattern") or rule.get("prefix") or "")
    return str(rule)


def _normalize(command: str) -> str:
    return " ".join(command.strip().split())


def powershellToolCheckExactMatchPermission(
    command: str,
    rules: list[str | dict[str, Any] | PowerShellPermissionRule],
) -> bool:
    normalized = _normalize(command)
    return any(normalized.casefold() == _pattern(rule).casefold() for rule in rules)


def powershellToolCheckPermission(
    command: str,
    rules: list[str | dict[str, Any] | PowerShellPermissionRule],
) -> bool:
    normalized = _normalize(command)
    lower = normalized.casefold()
    for rule in rules:
        pattern = _pattern(rule)
        if not pattern:
            continue
        if "*" in pattern and fnmatch.fnmatchcase(lower, pattern.casefold()):
            return True
        prefix = pattern.casefold()
        if lower == prefix or lower.startswith(prefix + " "):
            return True
    return False


async def powershellToolHasPermission(
    command: str,
    *,
    rules: list[str | dict[str, Any] | PowerShellPermissionRule] | None = None,
    read_only_mode: bool = False,
) -> dict[str, Any]:
    if read_only_mode:
        ok = isReadOnlyCommand(command)
        return {"allowed": ok, "reason": None if ok else "Command is not read-only."}
    if powershellToolCheckPermission(command, rules or []):
        return {"allowed": True, "reason": None}
    read_only = isReadOnlyCommand(command)
    warning = getDestructiveCommandWarning(command)
    suggestions = []
    head = command.strip().split(maxsplit=1)[0] if command.strip() else ""
    if head and not warning:
        suggestions.append(PowerShellPermissionRule(head, read_only=read_only).to_dict())
    return {"allowed": read_only, "reason": warning, "suggested_rules": suggestions}
