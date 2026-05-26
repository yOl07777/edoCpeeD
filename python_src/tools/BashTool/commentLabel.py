"""Extract user-facing labels from bash comments."""

from __future__ import annotations

import re
from typing import Any


async def extractBashCommentLabel(*args: Any, **kwargs: Any) -> str | None:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    for line in command.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        label = re.sub(r"^#+\s*", "", stripped).strip()
        if label:
            return label
    match = re.search(r"(?:^|\s)#\s*([^\n]+)$", command)
    return match.group(1).strip() if match else None


__all__ = ["extractBashCommentLabel"]
