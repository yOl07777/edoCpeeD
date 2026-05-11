from __future__ import annotations

import asyncio
import json
import subprocess
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


def _workflow_dir(path: str = ".deepseek_workflows", *, cwd: str | None = None):
    root = resolve_workspace_path(path, cwd=cwd)
    root.mkdir(parents=True, exist_ok=True)
    return root


async def workflow(
    action: str,
    *,
    name: str | None = None,
    command: str | None = None,
    workflows_dir: str = ".deepseek_workflows",
    cwd: str | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    root = _workflow_dir(workflows_dir, cwd=cwd)
    if action == "list":
        items = []
        for path in sorted(root.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append({"name": path.stem, "path": str(path), **data})
        return {"count": len(items), "workflows": items}
    if action == "save":
        if not name or not command:
            raise ValueError("name and command are required")
        path = root / f"{name}.json"
        path.write_text(json.dumps({"command": command}, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"name": name, "path": str(path), "command": command}
    if action == "run":
        if not name:
            raise ValueError("name is required")
        path = root / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        proc = await asyncio.to_thread(
            subprocess.run,
            data["command"],
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "name": name,
            "command": data["command"],
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    raise ValueError(f"Unknown workflow action: {action}")


WorkflowTool = PythonTool(
    name="workflow",
    description="List, save, or run local shell-command workflows.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["list", "save", "run"]},
            "name": {"type": "string"},
            "command": {"type": "string"},
            "workflows_dir": {"type": "string", "default": ".deepseek_workflows"},
            "timeout_seconds": {"type": "integer", "default": 60},
        },
        required=["action"],
    ),
    handler=workflow,
    read_only=False,
)
