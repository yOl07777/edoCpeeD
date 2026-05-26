from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def ShellDetailDialog(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(kwargs.get("task") or (args[0] if args else None), **kwargs)
    return task_payload("shell_detail_dialog", task=task, command=kwargs.get("command") or task["title"], output=kwargs.get("output", ""))


__all__ = ["ShellDetailDialog"]
