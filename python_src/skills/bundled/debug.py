from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerDebugSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("debug", "Investigate failures with focused repros, logs, and tests.", allowedTools=["Read", "Grep", "Bash", "Edit"])


__all__ = ["registerDebugSkill"]
