"""Local symbol extraction helpers for LSPTool."""

from __future__ import annotations

import re
from typing import Any

from python_src.tools.path_utils import resolve_workspace_path

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def getSymbolAtPosition(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    text = data.get("text")
    path = data.get("path")
    cwd = data.get("cwd")
    if text is None and path:
        text = resolve_workspace_path(str(path), cwd=str(cwd) if cwd else None).read_text(encoding="utf-8", errors="replace")
    text = str(text or "")
    line_number = int(data.get("line") or data.get("lineNumber") or 1)
    character = int(data.get("character") or data.get("column") or 0)
    lines = text.splitlines()
    if line_number < 1 or line_number > len(lines):
        return {"symbol": None, "line": line_number, "character": character, "range": None}
    line = lines[line_number - 1]
    for match in IDENT_RE.finditer(line):
        if match.start() <= character <= match.end():
            return {
                "symbol": match.group(0),
                "line": line_number,
                "character": character,
                "range": {"start": match.start(), "end": match.end()},
            }
    return {"symbol": None, "line": line_number, "character": character, "range": None}


__all__ = ["getSymbolAtPosition"]
