from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerUpdateConfigSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("update-config", "Update local DeepSeek Code configuration safely.", allowedTools=["Read", "Edit"])


__all__ = ["registerUpdateConfigSkill"]
