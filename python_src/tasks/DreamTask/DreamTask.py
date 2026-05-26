"""Background task state for auto-dream memory consolidation."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from python_src.Task import createTaskStateBase, generateTaskId
from python_src.services.autoDream.consolidationLock import rollbackConsolidationLock


MAX_TURNS = 30
SetAppState = Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None]


def isDreamTask(task: Any) -> bool:
    return isinstance(task, dict) and task.get("type") == "dream"


def _update_task(taskId: str, setAppState: SetAppState, updater: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
    def state_updater(prev: dict[str, Any]) -> dict[str, Any]:
        task = (prev.get("tasks") or {}).get(taskId)
        if not isDreamTask(task):
            return prev
        next_task = updater(task)
        if next_task is task or next_task == task:
            return prev
        next_state = dict(prev)
        tasks = dict(prev.get("tasks") or {})
        tasks[taskId] = next_task
        next_state["tasks"] = tasks
        return next_state

    setAppState(state_updater)


def registerDreamTask(
    setAppState: SetAppState,
    opts: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    options = {**(opts or {}), **kwargs}
    task_id = generateTaskId("dream")
    task = createTaskStateBase(task_id, "dream", "dreaming")
    task.update(
        {
            "status": "running",
            "phase": "starting",
            "sessionsReviewing": int(options.get("sessionsReviewing") or 0),
            "filesTouched": [],
            "turns": [],
            "abortController": options.get("abortController"),
            "priorMtime": float(options.get("priorMtime") or 0),
        }
    )

    def state_updater(prev: dict[str, Any]) -> dict[str, Any]:
        next_state = dict(prev)
        tasks = dict(prev.get("tasks") or {})
        tasks[task_id] = task
        next_state["tasks"] = tasks
        return next_state

    setAppState(state_updater)
    return task_id


def addDreamTurn(
    taskId: str,
    turn: dict[str, Any],
    touchedPaths: list[str] | None,
    setAppState: SetAppState,
) -> None:
    touched_paths = touchedPaths or []

    def updater(task: dict[str, Any]) -> dict[str, Any]:
        seen = set(task.get("filesTouched") or [])
        new_touched = [path for path in touched_paths if path not in seen and not seen.add(path)]
        text = str(turn.get("text") or "")
        tool_count = int(turn.get("toolUseCount") or 0)
        if not text and tool_count == 0 and not new_touched:
            return task
        next_task = dict(task)
        if new_touched:
            next_task["phase"] = "updating"
            next_task["filesTouched"] = list(task.get("filesTouched") or []) + new_touched
        next_task["turns"] = (list(task.get("turns") or []) + [{"text": text, "toolUseCount": tool_count}])[-MAX_TURNS:]
        return next_task

    _update_task(taskId, setAppState, updater)


def completeDreamTask(taskId: str, setAppState: SetAppState) -> None:
    def updater(task: dict[str, Any]) -> dict[str, Any]:
        next_task = dict(task)
        next_task.update({"status": "completed", "endTime": int(time.time() * 1000), "notified": True})
        next_task.pop("abortController", None)
        return next_task

    _update_task(taskId, setAppState, updater)


def failDreamTask(taskId: str, setAppState: SetAppState) -> None:
    def updater(task: dict[str, Any]) -> dict[str, Any]:
        next_task = dict(task)
        next_task.update({"status": "failed", "endTime": int(time.time() * 1000), "notified": True})
        next_task.pop("abortController", None)
        return next_task

    _update_task(taskId, setAppState, updater)


async def _kill(taskId: str, setAppState: SetAppState) -> None:
    prior: float | None = None

    def updater(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal prior
        if task.get("status") != "running":
            return task
        controller = task.get("abortController")
        abort = getattr(controller, "abort", None)
        if callable(abort):
            abort()
        prior = float(task.get("priorMtime") or 0)
        next_task = dict(task)
        next_task.update({"status": "killed", "endTime": int(time.time() * 1000), "notified": True})
        next_task.pop("abortController", None)
        return next_task

    _update_task(taskId, setAppState, updater)
    if prior is not None:
        await rollbackConsolidationLock(prior)


DreamTask: dict[str, Any] = {"name": "DreamTask", "type": "dream", "kill": _kill}


__all__ = [
    "DreamTask",
    "addDreamTurn",
    "completeDreamTask",
    "failDreamTask",
    "isDreamTask",
    "registerDreamTask",
]
