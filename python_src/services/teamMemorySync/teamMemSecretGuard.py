"""Secret guard for team memory writes."""

from __future__ import annotations

from typing import Any

from .secretScanner import scanForSecrets


async def checkTeamMemSecrets(*args: Any, **kwargs: Any) -> dict[str, Any]:
    content = str(kwargs.get("content") if "content" in kwargs else (args[0] if args else ""))
    path = str(kwargs.get("path") or kwargs.get("filePath") or (args[1] if len(args) > 1 else "memory.md"))
    matches = await scanForSecrets(content)
    return {"ok": not matches, "path": path, "matches": matches, "skipped": bool(matches)}


__all__ = ["checkTeamMemSecrets"]
