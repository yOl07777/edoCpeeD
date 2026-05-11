from __future__ import annotations

import re

from python_src.tools.PowerShellTool.readOnlyValidation import isReadOnlyCommand


UNSAFE_RE = re.compile(
    r"\b(Remove-Item|rm|del|erase|rmdir|Format-Volume|Clear-Disk|"
    r"Invoke-Expression|iex|Set-ExecutionPolicy|Start-Process|"
    r"git\s+(reset|clean|checkout|switch|commit|merge|rebase|pull|push|rm|add))\b",
    re.IGNORECASE,
)


def powershellCommandIsSafe(command: str) -> bool:
    if UNSAFE_RE.search(command):
        return False
    if ">" in command or ">>" in command:
        return False
    return isReadOnlyCommand(command)


async def powershellCommandIsSafeAsync(command: str) -> bool:
    return powershellCommandIsSafe(command)
