from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputHelpMenu(*args: Any, **kwargs: Any) -> Any:
    commands = kwargs.get("commands") or (args[0] if args else None) or ["/help", "/status", "/write", "/compact", "/exit"]
    return prompt_payload("prompt_input_help_menu", commands=[str(command) for command in commands], count=len(commands))


__all__ = ["PromptInputHelpMenu"]
