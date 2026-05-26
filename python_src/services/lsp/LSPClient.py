"""Lightweight local LSP client facade."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SYMBOL_RE = re.compile(
    r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)|^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)


class LocalLSPClient:
    def __init__(self, root: str | Path = ".", server: dict[str, Any] | None = None) -> None:
        self.root = Path(root).resolve()
        self.server = server or {"id": "local"}
        self.connected = True

    async def search_symbols(self, query: str, include: str = "**/*", limit: int = 100) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        extensions = set(self.server.get("extensions") or [".py", ".ts", ".tsx", ".js", ".jsx"])
        for path in self.root.glob(include):
            if len(results) >= limit:
                break
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in SYMBOL_RE.finditer(text):
                name = match.group(1) or match.group(2)
                if query.lower() in name.lower():
                    results.append({"path": str(path), "line": text.count("\n", 0, match.start()) + 1, "symbol": name})
                    if len(results) >= limit:
                        break
        return results

    async def shutdown(self) -> dict[str, Any]:
        self.connected = False
        return {"connected": False, "server": self.server.get("id")}


async def createLSPClient(root: str | Path = ".", server: dict[str, Any] | None = None) -> LocalLSPClient:
    return LocalLSPClient(root, server)
