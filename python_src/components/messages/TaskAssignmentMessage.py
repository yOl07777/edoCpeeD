from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def getTaskAssignmentSummary(*args: Any, **kwargs: Any) -> Any:
    task = text_from(args[0] if args else None, **kwargs)
    assignee = str(kwargs.get("assignee") or kwargs.get("agent") or "subagent")
    return f"Assigned to {assignee}: {task}"


async def TaskAssignmentDisplay(*args: Any, **kwargs: Any) -> Any:
    task = text_from(args[0] if args else None, **kwargs)
    assignee = str(kwargs.get("assignee") or kwargs.get("agent") or "subagent")
    return message_payload("task_assignment_display", task=task, assignee=assignee, summary=await getTaskAssignmentSummary(task, assignee=assignee))


async def tryRenderTaskAssignmentMessage(*args: Any, **kwargs: Any) -> Any:
    return await TaskAssignmentDisplay(*args, **kwargs)


__all__ = ["TaskAssignmentDisplay", "getTaskAssignmentSummary", "tryRenderTaskAssignmentMessage"]
