"""Local multi-agent spawn helpers."""

from __future__ import annotations

import re
from typing import Any

from python_src.tools.agent_store import create_agent


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "teammate"


async def generateUniqueTeammateName(*args: Any, **kwargs: Any) -> str:
    base = _slug(str(args[0] if args else kwargs.get("base") or kwargs.get("name") or "teammate"))
    existing = {str(name).lower() for name in (kwargs.get("existing") or kwargs.get("existing_names") or [])}
    if base not in existing:
        return base
    index = 2
    while f"{base}-{index}" in existing:
        index += 1
    return f"{base}-{index}"


async def resolveTeammateModel(*args: Any, **kwargs: Any) -> str:
    requested = kwargs.get("model") or (args[0] if args else None)
    return str(requested or kwargs.get("default_model") or "deepseek-chat")


async def spawnTeammate(*args: Any, **kwargs: Any) -> dict[str, Any]:
    name = await generateUniqueTeammateName(kwargs.get("name") or kwargs.get("base") or "teammate", existing=kwargs.get("existing", []))
    prompt = str(kwargs.get("prompt") or kwargs.get("instructions") or "")
    model = await resolveTeammateModel(kwargs.get("model"), default_model=kwargs.get("default_model", "deepseek-chat"))
    record = create_agent(name, prompt).to_dict()
    record.update({"model": model, "dry_run": True})
    return record


__all__ = ["generateUniqueTeammateName", "resolveTeammateModel", "spawnTeammate"]
