"""State selectors migrated from ``src/state/selectors.ts``."""

from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _task(app_state: dict[str, Any], task_id: str | None) -> dict[str, Any] | None:
    if not task_id:
        return None
    tasks = app_state.get("tasks") or {}
    return _as_dict(tasks.get(task_id))


def _is_in_process_teammate_task(task: dict[str, Any] | None) -> bool:
    if not task:
        return False
    return task.get("type") == "in_process_teammate"


def getViewedTeammateTask(appState: dict[str, Any]) -> dict[str, Any] | None:
    task = _task(appState, appState.get("viewingAgentTaskId"))
    return task if _is_in_process_teammate_task(task) else None


def getActiveAgentForInput(appState: dict[str, Any]) -> dict[str, Any]:
    viewed = getViewedTeammateTask(appState)
    if viewed is not None:
        return {"type": "viewed", "task": viewed}

    task = _task(appState, appState.get("viewingAgentTaskId"))
    if task and task.get("type") == "local_agent":
        return {"type": "named_agent", "task": task}

    return {"type": "leader"}


__all__ = ["getActiveAgentForInput", "getViewedTeammateTask"]
