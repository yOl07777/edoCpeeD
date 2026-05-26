from __future__ import annotations

import os
from typing import Any


CLI_SYSPROMPT_PREFIXES = {
    "default": "You are DeepSeek Code, a terminal coding assistant.",
    "analysis": "You are DeepSeek Code. Focus on concise, evidence-based code analysis.",
    "plan": "You are DeepSeek Code. Produce a practical implementation plan before editing.",
}


async def getAttributionHeader(*_args: Any, **kwargs: Any) -> str:
    name = str(kwargs.get("name") or os.getenv("DEEPSEEK_CODE_ATTRIBUTION") or "DeepSeek Code")
    return f"Generated with {name}"


async def getCLISyspromptPrefix(mode: Any = "default", *_args: Any, **kwargs: Any) -> str:
    key = str(kwargs.get("mode") or mode or "default")
    return CLI_SYSPROMPT_PREFIXES.get(key, CLI_SYSPROMPT_PREFIXES["default"])


__all__ = ["CLI_SYSPROMPT_PREFIXES", "getAttributionHeader", "getCLISyspromptPrefix"]
