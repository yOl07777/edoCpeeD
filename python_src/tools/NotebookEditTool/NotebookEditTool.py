from __future__ import annotations

import json
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


async def notebook_edit(
    path: str,
    cell_index: int,
    source: str,
    *,
    cwd: str | None = None,
    cell_type: str | None = None,
) -> dict[str, Any]:
    target = resolve_workspace_path(path, cwd=cwd)
    notebook = json.loads(target.read_text(encoding="utf-8"))
    cells = notebook.setdefault("cells", [])
    if cell_index < 0:
        raise IndexError("cell_index must be non-negative")
    while len(cells) <= cell_index:
        cells.append({"cell_type": cell_type or "code", "metadata": {}, "source": []})
    cell = cells[cell_index]
    if cell_type:
        cell["cell_type"] = cell_type
    cell["source"] = source.splitlines(keepends=True)
    target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    return {
        "path": str(target),
        "cell_index": cell_index,
        "cell_type": cell.get("cell_type"),
        "cell_count": len(cells),
    }


inputSchema = object_schema(
    {
        "path": {"type": "string"},
        "cell_index": {"type": "integer"},
        "source": {"type": "string"},
        "cell_type": {"type": "string", "enum": ["code", "markdown", "raw"]},
    },
    required=["path", "cell_index", "source"],
)
outputSchema = {"type": "object"}

NotebookEditTool = PythonTool(
    name="notebook_edit",
    description="Create or replace a cell in a Jupyter .ipynb file.",
    parameters=inputSchema,
    handler=notebook_edit,
    read_only=False,
)
