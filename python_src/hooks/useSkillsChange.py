from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useSkillsChange(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    before = {str(item) for item in listify(pick(options, "before", "previous", default=[]))}
    after = {str(item) for item in listify(pick(options, "after", "current", default=[]))}
    return {
        "provider": "deepseek",
        "added": sorted(after - before),
        "removed": sorted(before - after),
        "changed": before != after,
    }
