from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import AGENT_SOURCES


async def getAgentSourceDisplayName(*args: Any, **kwargs: Any) -> Any:
    source = kwargs.get("source") or (args[0] if args else "")
    return AGENT_SOURCES.get(str(source), str(source) or "Unknown")


__all__ = ["getAgentSourceDisplayName"]
