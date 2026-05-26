"""Helpers for switching between leader and teammate transcript views."""

from __future__ import annotations

import time
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from python_src.Task import isTerminalTaskStatus


PANEL_GRACE_MS = 30_000


def _now_ms() -> int:
    return int(time.time() * 1000)


def _is_local_agent(task: Any) -> bool:
    return isinstance(task, dict) and task.get("type") == "local_agent"


def _release(task: dict[str, Any]) -> dict[str, Any]:
    released = dict(task)
    released["retain"] = False
    released["messages"] = None
    released["diskLoaded"] = False
    released["evictAfter"] = (
        _now_ms() + PANEL_GRACE_MS if isTerminalTaskStatus(str(task.get("status"))) else None
    )
    return released


def enterTeammateView(taskId: str, setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None]) -> None:
    def updater(prev: dict[str, Any]) -> dict[str, Any]:
        task = (prev.get("tasks") or {}).get(taskId)
        prev_id = prev.get("viewingAgentTaskId")
        prev_task = (prev.get("tasks") or {}).get(prev_id) if prev_id else None
        switching = (
            prev_id is not None
            and prev_id != taskId
            and _is_local_agent(prev_task)
            and bool(prev_task.get("retain"))
        )
        needs_retain = _is_local_agent(task) and (not task.get("retain") or task.get("evictAfter") is not None)
        needs_view = prev.get("viewingAgentTaskId") != taskId or prev.get("viewSelectionMode") != "viewing-agent"
        if not needs_retain and not needs_view and not switching:
            return prev

        next_state = deepcopy(prev)
        next_state["viewingAgentTaskId"] = taskId
        next_state["viewSelectionMode"] = "viewing-agent"
        tasks = dict(next_state.get("tasks") or {})
        if switching and isinstance(prev_task, dict):
            tasks[prev_id] = _release(prev_task)
        if needs_retain and isinstance(task, dict):
            retained = dict(task)
            retained["retain"] = True
            retained["evictAfter"] = None
            tasks[taskId] = retained
        next_state["tasks"] = tasks
        return next_state

    setAppState(updater)


def exitTeammateView(setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None]) -> None:
    def updater(prev: dict[str, Any]) -> dict[str, Any]:
        task_id = prev.get("viewingAgentTaskId")
        if task_id is None and prev.get("viewSelectionMode") == "none":
            return prev
        next_state = deepcopy(prev)
        next_state["viewingAgentTaskId"] = None
        next_state["viewSelectionMode"] = "none"
        if task_id is not None:
            task = (prev.get("tasks") or {}).get(task_id)
            if _is_local_agent(task) and task.get("retain"):
                tasks = dict(next_state.get("tasks") or {})
                tasks[task_id] = _release(task)
                next_state["tasks"] = tasks
        return next_state

    setAppState(updater)


def stopOrDismissAgent(taskId: str, setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None]) -> None:
    def updater(prev: dict[str, Any]) -> dict[str, Any]:
        task = (prev.get("tasks") or {}).get(taskId)
        if not _is_local_agent(task):
            return prev
        if task.get("status") == "running":
            controller = task.get("abortController")
            abort = getattr(controller, "abort", None)
            if callable(abort):
                abort()
            elif isinstance(controller, dict) and callable(controller.get("abort")):
                controller["abort"]()
            return prev
        if task.get("evictAfter") == 0:
            return prev

        next_state = deepcopy(prev)
        tasks = dict(next_state.get("tasks") or {})
        dismissed = _release(task)
        dismissed["evictAfter"] = 0
        tasks[taskId] = dismissed
        next_state["tasks"] = tasks
        if prev.get("viewingAgentTaskId") == taskId:
            next_state["viewingAgentTaskId"] = None
            next_state["viewSelectionMode"] = "none"
        return next_state

    setAppState(updater)


__all__ = ["enterTeammateView", "exitTeammateView", "stopOrDismissAgent"]
