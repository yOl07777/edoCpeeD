from __future__ import annotations

import re


def isDotGitPathPS(path: str) -> bool:
    normalized = path.replace("\\", "/").lower().strip("'\"")
    return normalized == ".git" or normalized.endswith("/.git") or "/.git/" in normalized


def isGitInternalPathPS(path: str) -> bool:
    normalized = path.replace("\\", "/").lower().strip("'\"")
    return bool(re.search(r"(^|/)\.git/(objects|refs|hooks|logs|index|config|head)(/|$)", normalized))
