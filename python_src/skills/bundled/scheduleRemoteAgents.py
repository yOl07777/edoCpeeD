from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerScheduleRemoteAgentsSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("schedule-remote-agents", "Create a local dry-run plan for scheduled remote agent work.", userInvocable=False)


__all__ = ["registerScheduleRemoteAgentsSkill"]
