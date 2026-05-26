from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


def _task_id(item: Any) -> str:
    return str(item.get("id", item) if isinstance(item, dict) else item)


async def useTaskListWatcher(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    previous = {_task_id(item) for item in listify(pick(options, "previous", default=[]))}
    current_items = listify(pick(options, "tasks", "current", default=[]))
    current = {_task_id(item) for item in current_items}
    return {
        "provider": "deepseek",
        "tasks": current_items,
        "added": sorted(current - previous),
        "removed": sorted(previous - current),
        "changed": current != previous,
    }
