from __future__ import annotations

import re


CMDLET_ALLOWLIST = {
    "cat": "Get-Content",
    "cd": "Set-Location",
    "compare-object": "Compare-Object",
    "dir": "Get-ChildItem",
    "echo": "Write-Output",
    "findstr": "Select-String",
    "gc": "Get-Content",
    "gci": "Get-ChildItem",
    "get-childitem": "Get-ChildItem",
    "get-command": "Get-Command",
    "get-content": "Get-Content",
    "get-date": "Get-Date",
    "get-item": "Get-Item",
    "get-location": "Get-Location",
    "get-member": "Get-Member",
    "get-process": "Get-Process",
    "get-service": "Get-Service",
    "ls": "Get-ChildItem",
    "measure-object": "Measure-Object",
    "pwd": "Get-Location",
    "resolve-path": "Resolve-Path",
    "select-object": "Select-Object",
    "select-string": "Select-String",
    "sort-object": "Sort-Object",
    "tee-object": "Tee-Object",
    "where-object": "Where-Object",
    "write-output": "Write-Output",
}
MUTATING_RE = re.compile(
    r"\b(Remove-Item|rm|rmdir|del|erase|Move-Item|mv|Copy-Item|cp|"
    r"Set-Content|Add-Content|Out-File|New-Item|ni|Set-Item|Set-Location|"
    r"Start-Process|Invoke-Expression|iex|Invoke-WebRequest|iwr|curl|"
    r"git\s+(reset|clean|checkout|switch|commit|merge|rebase|pull|push|rm|add))\b",
    re.IGNORECASE,
)


def _command_head(statement: str) -> str:
    stripped = statement.strip()
    if not stripped:
        return ""
    return stripped.split()[0].strip("&").lower()


def resolveToCanonical(command: str) -> str:
    head = command.strip().lower()
    return CMDLET_ALLOWLIST.get(head, command.strip())


def isCwdChangingCmdlet(command: str) -> bool:
    return _command_head(command) in {"cd", "set-location", "push-location", "pop-location", "sl"}


def argLeaksValue(arg: str) -> bool:
    return bool(re.search(r"(password|passwd|secret|token|apikey|api_key)\s*[:=]", arg, re.IGNORECASE))


def isSafeOutputCommand(command: str) -> bool:
    head = _command_head(command)
    if head == "tee-object":
        return False
    return head in {"select-object", "sort-object", "where-object", "measure-object", "write-output"}


def isAllowlistedCommand(command: str) -> bool:
    head = _command_head(command)
    if not head:
        return False
    return head in CMDLET_ALLOWLIST and not isCwdChangingCmdlet(command)


def isAllowlistedPipelineTail(command: str) -> bool:
    return all(isSafeOutputCommand(part) or isAllowlistedCommand(part) for part in command.split("|")[1:])


def hasSyncSecurityConcerns(command: str) -> bool:
    if ">" in command or ">>" in command:
        return True
    if any(argLeaksValue(part) for part in command.split()):
        return True
    return bool(MUTATING_RE.search(command))


def isProvablySafeStatement(statement: str) -> bool:
    if hasSyncSecurityConcerns(statement):
        return False
    parts = [part.strip() for part in statement.split("|") if part.strip()]
    if not parts:
        return False
    return isAllowlistedCommand(parts[0]) and all(
        isSafeOutputCommand(part) or isAllowlistedCommand(part) for part in parts[1:]
    )


def isReadOnlyCommand(command: str) -> bool:
    statements = [part.strip() for part in re.split(r";|\r?\n", command) if part.strip()]
    return bool(statements) and all(isProvablySafeStatement(statement) for statement in statements)
