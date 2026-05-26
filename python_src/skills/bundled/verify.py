from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerVerifySkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("verify", "Design and run verification steps for a completed change.", allowedTools=["Read", "Grep", "Bash"])


__all__ = ["registerVerifySkill"]
