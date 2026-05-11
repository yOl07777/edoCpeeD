from __future__ import annotations

import re
from typing import Any


COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)


def detectGitOperation(command: str) -> dict[str, Any]:
    words = command.strip().split()
    if not words or words[0] != "git":
        return {"is_git": False, "operation": None}
    operation = words[1] if len(words) > 1 else None
    return {"is_git": True, "operation": operation}


def parseGitCommitId(text: str) -> str | None:
    match = COMMIT_RE.search(text)
    return match.group(0) if match else None


def trackGitOperations(command: str, output: str = "") -> dict[str, Any]:
    detected = detectGitOperation(command)
    return {
        **detected,
        "commit_id": parseGitCommitId(output),
    }
