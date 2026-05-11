from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


async def output_style(
    action: str,
    *,
    name: str | None = None,
    styles_dir: str = ".deepseek_output_styles",
    cwd: str | None = None,
) -> dict[str, Any]:
    root = resolve_workspace_path(styles_dir, cwd=cwd)
    root.mkdir(parents=True, exist_ok=True)
    if action == "list":
        styles = [{"name": path.stem, "path": str(path)} for path in sorted(root.glob("*.md"))]
        return {"count": len(styles), "styles": styles}
    if action == "read":
        if not name:
            raise ValueError("name is required")
        path = root / f"{name}.md"
        return {"name": name, "path": str(path), "content": path.read_text(encoding="utf-8", errors="replace")}
    raise ValueError(f"Unknown output_style action: {action}")


call = PythonTool(
    name="output_style",
    description="List or read local output style markdown files.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["list", "read"]},
            "name": {"type": "string"},
            "styles_dir": {"type": "string", "default": ".deepseek_output_styles"},
        },
        required=["action"],
    ),
    handler=output_style,
    read_only=True,
)
