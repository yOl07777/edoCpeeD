from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerStuckSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("stuck", "Unblock a stalled task by reframing evidence, assumptions, and next tests.", allowedTools=["Read", "Grep", "Bash"])


__all__ = ["registerStuckSkill"]
