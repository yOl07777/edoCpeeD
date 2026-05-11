from __future__ import annotations

import re


_WARNINGS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bRemove-Item\b|\brm\b|\bdel\b|\berase\b", re.IGNORECASE), "PowerShell removal commands can delete workspace files."),
    (re.compile(r"\bRemove-Item\b[^\n;]*\s-Recurse\b", re.IGNORECASE), "Recursive Remove-Item can delete entire directory trees."),
    (re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE), "git reset --hard discards local changes."),
    (re.compile(r"\bgit\s+clean\b", re.IGNORECASE), "git clean can delete untracked files."),
    (re.compile(r"\bFormat-Volume\b|\bClear-Disk\b", re.IGNORECASE), "Disk formatting commands are destructive."),
    (re.compile(r"\bInvoke-Expression\b|\biex\b", re.IGNORECASE), "Invoke-Expression executes generated text as code."),
    (re.compile(r"\bSet-ExecutionPolicy\b", re.IGNORECASE), "Changing execution policy affects system script safety."),
]


def getDestructiveCommandWarning(command: str) -> str | None:
    for pattern, warning in _WARNINGS:
        if pattern.search(command):
            return warning
    return None
