from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerClaudeApiSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("deepseek-api", "Help migrate Claude API usage to DeepSeek/OpenAI compatible APIs.", aliases=["claude-api"], allowedTools=["Read", "Grep", "Edit"])


__all__ = ["registerClaudeApiSkill"]
