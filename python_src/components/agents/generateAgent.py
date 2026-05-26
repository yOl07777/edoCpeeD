from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import slugify_agent_name


AGENT_CREATION_SYSTEM_PROMPT = """You are an elite DeepSeek Code agent architect.
Create concise, reliable subagent definitions that can be saved as markdown files.
Return JSON with identifier, whenToUse, and systemPrompt when a model client is used."""


async def generateAgent(*args: Any, **kwargs: Any) -> Any:
    user_prompt = str(kwargs.get("userPrompt") or (args[0] if args else "") or "specialized coding help")
    existing = set(kwargs.get("existingIdentifiers") or (args[2] if len(args) > 2 else []) or [])
    base = slugify_agent_name(user_prompt)[:50].strip("-")
    identifier = base or "deepseek-agent"
    counter = 2
    while identifier in existing:
        suffix = f"-{counter}"
        identifier = f"{base[:50 - len(suffix)]}{suffix}".strip("-")
        counter += 1
    return {
        "provider": "deepseek",
        "identifier": identifier,
        "whenToUse": f"Use this agent when the user asks for {user_prompt}.",
        "systemPrompt": (
            "You are a focused DeepSeek Code subagent. "
            f"Your responsibility is to handle requests about: {user_prompt}. "
            "Work carefully, state assumptions, use tools only when useful, and return concise actionable results."
        ),
        "systemPromptTemplate": AGENT_CREATION_SYSTEM_PROMPT,
        "model": kwargs.get("model") or (args[1] if len(args) > 1 else "deepseek-chat"),
    }


__all__ = ["AGENT_CREATION_SYSTEM_PROMPT", "generateAgent"]
