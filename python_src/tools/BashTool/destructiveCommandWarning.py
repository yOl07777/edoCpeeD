from __future__ import annotations

import re


_WARNINGS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\brm\s+-[^\n;|&]*[rf]", re.IGNORECASE), "Recursive or forced removal can delete many files."),
    (re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE), "git reset --hard discards local changes."),
    (re.compile(r"\bgit\s+clean\b", re.IGNORECASE), "git clean can delete untracked files."),
    (re.compile(r"\bchmod\s+-R\b|\bchown\s+-R\b", re.IGNORECASE), "Recursive permission changes are hard to undo."),
    (re.compile(r"\bdd\s+.*\bof=", re.IGNORECASE), "dd can overwrite disks or files."),
    (re.compile(r"\bmkfs\b", re.IGNORECASE), "mkfs formats a filesystem."),
    (re.compile(r"\bcurl\b.+\|\s*(sh|bash)|\bwget\b.+\|\s*(sh|bash)", re.IGNORECASE), "Piping downloaded code to a shell is risky."),
]


def getDestructiveCommandWarning(command: str) -> str | None:
    for pattern, warning in _WARNINGS:
        if pattern.search(command):
            return warning
    return None
