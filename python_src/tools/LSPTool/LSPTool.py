from __future__ import annotations

import re
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


SYMBOL_RE = re.compile(
    r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)|^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)


async def lsp_symbol_search(
    query: str,
    *,
    path: str = ".",
    include: str = "**/*",
    cwd: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    root = resolve_workspace_path(path, cwd=cwd)
    results: list[dict[str, Any]] = []
    for file_path in root.glob(include):
        if len(results) >= limit:
            break
        if not file_path.is_file() or file_path.suffix.lower() not in {".py", ".ts", ".tsx", ".js"}:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        for match in SYMBOL_RE.finditer(text):
            name = match.group(1) or match.group(2)
            if query.lower() in name.lower():
                line = text.count("\n", 0, match.start()) + 1
                results.append({"path": str(file_path), "line": line, "symbol": name})
                if len(results) >= limit:
                    break
    return {"query": query, "results": results, "count": len(results)}


LSPTool = PythonTool(
    name="lsp_symbol_search",
    description="Search Python/TypeScript files for function and class symbols.",
    parameters=object_schema(
        {
            "query": {"type": "string"},
            "path": {"type": "string", "default": "."},
            "include": {"type": "string", "default": "**/*"},
            "limit": {"type": "integer", "default": 100},
        },
        required=["query"],
    ),
    handler=lsp_symbol_search,
    read_only=True,
)
