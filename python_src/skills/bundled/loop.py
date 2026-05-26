from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerLoopSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("loop", "Run a tight implement-test-fix loop until the task is resolved.", allowedTools=["Read", "Edit", "Bash"])


__all__ = ["registerLoopSkill"]
