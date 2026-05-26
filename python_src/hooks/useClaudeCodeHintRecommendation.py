from __future__ import annotations

from typing import Any


async def useClaudeCodeHintRecommendation(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    shown = bool(kwargs.get("shown", False))
    command_count = int(kwargs.get("commandCount", kwargs.get("command_count", 0)) or 0)
    recommend = command_count >= int(kwargs.get("threshold", 3) or 3) and not shown
    return {
        "provider": "deepseek",
        "recommend": recommend,
        "message": "Tip: use DeepSeek Code slash commands for repeat workflows." if recommend else "",
    }


__all__ = ["useClaudeCodeHintRecommendation"]
