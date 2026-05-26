from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def AgentProgressLine(*args: Any, **kwargs: Any) -> Any:
    message = str(option(args, kwargs, "message", scalar_arg(args, "Agent working")))
    status = str(option(args, kwargs, "status", "running"))
    agent = str(option(args, kwargs, "agent", option(args, kwargs, "name", "agent")))
    return component_payload("agent_progress_line", agent=agent, status=status, message=message, active=status not in {"done", "failed"})


__all__ = ["AgentProgressLine"]
