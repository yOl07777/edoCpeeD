from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any


DEEPSEEK_CODE_DOCS_MAP_URL = "https://api-docs.deepseek.com"
CLAUDE_CODE_DOCS_MAP_URL = DEEPSEEK_CODE_DOCS_MAP_URL
SYSTEM_PROMPT_DYNAMIC_BOUNDARY = "<deepseek-code-env>"
DEFAULT_AGENT_PROMPT = (
    "You are a focused DeepSeek Code subagent. Complete the assigned coding task, "
    "respect the existing repository, and report changed files plus verification."
)


async def getUnameSR(*_args: Any, **_kwargs: Any) -> str:
    return f"{platform.system()} {platform.release()} {platform.machine()}".strip()


async def computeSimpleEnvInfo(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    cwd = Path(str(kwargs.get("cwd") or os.getcwd()))
    return {
        "cwd": str(cwd),
        "os": await getUnameSR(),
        "shell": os.getenv("SHELL") or os.getenv("ComSpec") or "",
        "provider": "deepseek",
        "model": kwargs.get("model") or os.getenv("DEFAULT_MODEL") or "deepseek-chat",
    }


async def computeEnvInfo(*args: Any, **kwargs: Any) -> dict[str, Any]:
    info = await computeSimpleEnvInfo(*args, **kwargs)
    info.update(
        {
            "api_keys_configured": bool(os.getenv("DEEPSEEK_API_KEYS") or os.getenv("DEEPSEEK_API_KEY")),
            "endpoints": [item.strip() for item in os.getenv("DEEPSEEK_ENDPOINTS", "https://api.deepseek.com/v1").split(",") if item.strip()],
            "workspace": kwargs.get("workspace") or info["cwd"],
        }
    )
    return info


async def prependBullets(items: Any = None, *_args: Any, **_kwargs: Any) -> str:
    if items is None:
        return ""
    if isinstance(items, str):
        rows = [line for line in items.splitlines() if line.strip()]
    else:
        rows = [str(item) for item in items]
    return "\n".join(f"- {row}" for row in rows)


async def getScratchpadInstructions(*_args: Any, **_kwargs: Any) -> str:
    return (
        "Use a private scratchpad for reasoning if needed, but keep the final answer concise. "
        "Do not expose hidden chain-of-thought; summarize decisions and verification instead."
    )


async def getSystemPrompt(*_args: Any, **kwargs: Any) -> str:
    env = await computeEnvInfo(**kwargs)
    return "\n".join(
        [
            "You are DeepSeek Code, a Python terminal coding assistant.",
            "Use OpenAI-compatible DeepSeek chat messages and tool calls.",
            "Preserve the original src TypeScript tree unless explicitly asked to modify it.",
            await getScratchpadInstructions(),
            f"{SYSTEM_PROMPT_DYNAMIC_BOUNDARY}",
            await prependBullets([f"{key}: {value}" for key, value in env.items()]),
            f"{SYSTEM_PROMPT_DYNAMIC_BOUNDARY}",
        ]
    )


async def enhanceSystemPromptWithEnvDetails(prompt: Any = "", *_args: Any, **kwargs: Any) -> str:
    base = str(prompt or await getSystemPrompt(**kwargs))
    env = await computeEnvInfo(**kwargs)
    details = await prependBullets([f"{key}: {value}" for key, value in env.items()])
    return f"{base}\n\nEnvironment:\n{details}"


__all__ = [
    "CLAUDE_CODE_DOCS_MAP_URL",
    "DEEPSEEK_CODE_DOCS_MAP_URL",
    "DEFAULT_AGENT_PROMPT",
    "SYSTEM_PROMPT_DYNAMIC_BOUNDARY",
    "computeEnvInfo",
    "computeSimpleEnvInfo",
    "enhanceSystemPromptWithEnvDetails",
    "getScratchpadInstructions",
    "getSystemPrompt",
    "getUnameSR",
    "prependBullets",
]
