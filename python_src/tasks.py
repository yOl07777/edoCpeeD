from __future__ import annotations

from typing import Any


def _task(name: str, type: str) -> dict[str, Any]:
    async def kill(taskId: str, setAppState: Any = None) -> None:
        if callable(setAppState):
            setAppState(lambda prev: prev)

    return {"name": name, "type": type, "kill": kill}


def getAllTasks() -> list[dict[str, Any]]:
    return [
        _task("LocalShellTask", "local_bash"),
        _task("LocalAgentTask", "local_agent"),
        _task("RemoteAgentTask", "remote_agent"),
        _task("InProcessTeammateTask", "in_process_teammate"),
        _task("LocalWorkflowTask", "local_workflow"),
        _task("MonitorMcpTask", "monitor_mcp"),
        _task("DreamTask", "dream"),
    ]


def getTaskByType(type: str) -> dict[str, Any] | None:
    return next((task for task in getAllTasks() if task["type"] == type), None)
