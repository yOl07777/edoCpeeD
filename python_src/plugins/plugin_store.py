from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from python_src.tools.path_utils import resolve_workspace_path


def discover_plugins(root: str = ".", *, cwd: str | None = None) -> list[dict[str, Any]]:
    base = resolve_workspace_path(root, cwd=cwd)
    plugins: list[dict[str, Any]] = []
    for manifest in base.rglob(".codex-plugin/plugin.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        plugins.append({"path": str(manifest), **data})
    return plugins
