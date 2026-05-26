from __future__ import annotations

from typing import Any

from python_src.components.agents.generateAgent import generateAgent


async def GenerateStep(*args: Any, **kwargs: Any) -> Any:
    return await generateAgent(kwargs.get("userPrompt") or (args[0] if args else "specialized coding help"), kwargs.get("model", "deepseek-chat"), kwargs.get("existingIdentifiers", []))


__all__ = ["GenerateStep"]
