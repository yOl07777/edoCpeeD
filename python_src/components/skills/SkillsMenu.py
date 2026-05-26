from __future__ import annotations

from typing import Any


async def SkillsMenu(*args: Any, **kwargs: Any) -> Any:
    skills = kwargs.get("skills") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "").lower()
    rows = []
    for index, skill in enumerate(skills):
        if isinstance(skill, dict):
            name = str(skill.get("name") or skill.get("id") or f"skill-{index}")
            description = str(skill.get("description") or "")
        else:
            name = str(skill)
            description = ""
        if not query or query in name.lower() or query in description.lower():
            rows.append({"index": index, "name": name, "description": description})
    return {"type": "skills_menu", "provider": "deepseek", "skills": rows, "count": len(rows), "query": query}


__all__ = ["SkillsMenu"]
