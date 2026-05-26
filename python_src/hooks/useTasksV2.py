from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useTasksV2(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    tasks = listify(pick(options, "tasks", default=[]))
    active = [task for task in tasks if not (isinstance(task, dict) and task.get("done"))]
    selected_index = max(0, min(int(pick(options, "selectedIndex", default=0)), len(tasks) - 1)) if tasks else -1
    return {"provider": "deepseek", "tasks": tasks, "active": active, "selectedIndex": selected_index, "count": len(tasks)}

async def useTasksV2WithCollapseEffect(*args: Any, **kwargs: Any) -> Any:
    state = await useTasksV2(*args, **kwargs)
    options = first_mapping(*args, kwargs)
    collapsed_ids = {str(item) for item in listify(pick(options, "collapsed", "collapsedIds", default=[]))}
    state["collapsedIds"] = sorted(collapsed_ids)
    state["visibleTasks"] = [
        task for task in state["tasks"] if str(task.get("id", task) if isinstance(task, dict) else task) not in collapsed_ids
    ]
    return state
