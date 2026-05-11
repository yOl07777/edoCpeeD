from __future__ import annotations

from pathlib import Path
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path


def _find_skill_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("SKILL.md"))


async def skill(
    action: str,
    *,
    name: str | None = None,
    skills_dir: str = ".codex/skills",
    cwd: str | None = None,
    max_chars: int = 20_000,
) -> dict[str, Any]:
    root = resolve_workspace_path(skills_dir, cwd=cwd)
    files = _find_skill_files(root)
    if action == "list":
        return {
            "skills": [
                {"name": path.parent.name, "path": str(path)}
                for path in files
            ]
        }
    if action == "read":
        if not name:
            raise ValueError("name is required for read")
        for path in files:
            if path.parent.name == name:
                text = path.read_text(encoding="utf-8", errors="replace")
                return {"name": name, "path": str(path), "content": text[:max_chars], "truncated": len(text) > max_chars}
        raise FileNotFoundError(f"Skill not found: {name}")
    raise ValueError(f"Unknown skill action: {action}")


inputSchema = object_schema(
    {
        "action": {"type": "string", "enum": ["list", "read"]},
        "name": {"type": "string"},
        "skills_dir": {"type": "string", "default": ".codex/skills"},
    },
    required=["action"],
)
outputSchema = {"type": "object"}

SkillTool = PythonTool(
    name="skill",
    description="List or read local skills from a workspace skills directory.",
    parameters=inputSchema,
    handler=skill,
    read_only=True,
)
