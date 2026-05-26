from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerSimplifySkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("simplify", "Simplify code or prose while preserving behavior and intent.", allowedTools=["Read", "Edit"])


__all__ = ["registerSimplifySkill"]
