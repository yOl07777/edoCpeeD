from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def formatToolUseSummary(*args: Any, **kwargs: Any) -> Any:
    tools = kwargs.get("tools") or (args[0] if args else []) or []
    names = [str(tool.get("name") if isinstance(tool, dict) else tool) for tool in tools]
    return ", ".join(names)


async def RemoteSessionDetailDialog(*args: Any, **kwargs: Any) -> Any:
    session = normalize_task(kwargs.get("session") or (args[0] if args else None), **kwargs)
    return task_payload("remote_session_detail_dialog", session=session, toolSummary=await formatToolUseSummary(session["tools"]))


__all__ = ["RemoteSessionDetailDialog", "formatToolUseSummary"]
