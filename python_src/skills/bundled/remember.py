from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerRememberSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("remember", "Capture durable project memory in local DeepSeek memory files.", allowedTools=["Read", "Edit"])


__all__ = ["registerRememberSkill"]
