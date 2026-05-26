from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerClaudeInChromeSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("deepseek-in-browser", "Prepare browser integration guidance without launching external flows.", aliases=["claude-in-chrome"])


__all__ = ["registerClaudeInChromeSkill"]
