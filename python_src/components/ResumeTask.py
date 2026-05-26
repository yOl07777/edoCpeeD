from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def ResumeTask(*args: Any, **kwargs: Any) -> Any:
    task = option(args, kwargs, "task", scalar_arg(args, first_options(args)))
    title = str(task.get("title", task.get("id", "task")) if isinstance(task, dict) else task)
    return component_payload("resume_task", task=task, title=title, resumable=bool(option(args, kwargs, "resumable", True)))


__all__ = ["ResumeTask"]
