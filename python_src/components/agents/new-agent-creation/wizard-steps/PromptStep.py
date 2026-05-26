from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def PromptStep(*args: Any, **kwargs: Any) -> Any:
    value = str(kwargs.get("systemPrompt") or kwargs.get("prompt") or (args[0] if args else "") or "")
    return component_result("agent_wizard_prompt_step", field="systemPrompt", value=value, complete=len(value) >= 20)


__all__ = ["PromptStep"]
