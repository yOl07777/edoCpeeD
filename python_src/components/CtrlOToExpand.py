from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def CtrlOToExpand(*args: Any, **kwargs: Any) -> Any:
    expanded = bool(option(args, kwargs, "expanded", False))
    return component_payload("ctrl_o_to_expand", expanded=expanded, hint="Ctrl+O expands subagent details")


async def SubAgentProvider(*args: Any, **kwargs: Any) -> Any:
    agent = option(args, kwargs, "agent", scalar_arg(args, {}))
    return component_payload("sub_agent_provider", agent=agent, available=bool(agent))


async def ctrlOToExpand(*args: Any, **kwargs: Any) -> Any:
    key = str(option(args, kwargs, "key", scalar_arg(args, ""))).lower()
    return key in {"ctrl+o", "ctrl-o", "\x0f"}


__all__ = ["CtrlOToExpand", "SubAgentProvider", "ctrlOToExpand"]
