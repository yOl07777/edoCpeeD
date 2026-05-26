from __future__ import annotations

from typing import Any

from ._basic import first_mapping, merge_dicts, pick


async def useSettings(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    defaults = pick(options, "defaults", default={}) or {}
    project = pick(options, "project", "projectSettings", default={}) or {}
    user = pick(options, "user", "userSettings", default={}) or {}
    settings = merge_dicts(defaults, user, project)
    settings.setdefault("provider", "deepseek")
    return {"provider": "deepseek", "settings": settings, "sources": ["defaults", "user", "project"]}
